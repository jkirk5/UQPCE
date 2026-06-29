import openmdao.api as om
import numpy as np
from openmdao.utils.assert_utils import assert_check_partials
from uqpce.mdao.uqpcegroup import UQPCEGroup
from uqpce.mdao import interface

#Import ExplicitComponents
from aero import AeroDiscipline
from WeightsComp import Weights_Struct
from propAndCost import Propulsion
from propAndCost import EngineWeight
from propAndCost import DOC
from BreguetRangeComp import BreguetRangeComp
from total_mass_comp import TotalMassComp

class AeroStruct(om.Group):
    """
    Coupled solver loop with AeroComp, WeightsComp, TotalMassComp, and BreguetRangeComp
    """
    def initialize(self):
        self.options.declare('vec_size', types=int)
    
    def setup(self):
        vec_size = self.options['vec_size']
        
        self.add_subsystem('aero', AeroDiscipline(vec_size=vec_size), 
                           promotes_inputs= ['S', 'AR', 'V', 'rho', 'g', 'C_D0_base', 'ks_base', 'e_base', 'S_0', 'm_total', 'delta_CD0', 'delta_ks', 'delta_e'], 
                           promotes_outputs= ['LD', 'CL'])    
    
        self.add_subsystem('mass', Weights_Struct(vec_size=vec_size), 
                           promotes_inputs= ['S', 'AR', ('V_cruise', 'V'), 'm_engine', 'm_total', 'm_fuse', 'kw_base', 'fsys_base', 'p_base', 'V_ref', 'delta_kw', 'delta_fsys', 'delta_p'], 
                           promotes_outputs= ['m_empty'])
        
        self.add_subsystem('total_mass', TotalMassComp(vec_size=vec_size), 
                           promotes_inputs= ['m_empty', 'm_fuel', 'm_payload'], 
                           promotes_outputs= ['m_total'])
        
        self.add_subsystem('range', BreguetRangeComp(vec_size=vec_size), 
                           promotes_inputs= ['LD', 'SFC', 'V', 'm_total', 'm_fuel'], 
                           promotes_outputs= [('R', 'R_comp')])
        
        #BalanceComp to determine converged value for 'm_fuel'
        bal = self.add_subsystem('range_bal', om.BalanceComp(), promotes=['*'])
        bal.add_balance(name='m_fuel', eq_units='m', lhs_name='R_comp', rhs_name='R_target', units='kg', shape=(resp_cnt,))

        #Setup solvers (linear + nonlinear)
        self.nonlinear_solver = om.NewtonSolver(solve_subsystems=True)
        self.nonlinear_solver.options['iprint'] = 2
        self.nonlinear_solver.options['maxiter'] = 20
        # self.nonlinear_solver.options['atol'] = 1e-6
        # self.nonlinear_solver.options['rtol'] = 1e-9
        self.linear_solver = om.DirectSolver()

if __name__ == '__main__':
    
    #Input files
    input_file = 'input.yaml'
    matrix_file = 'run_matrix_generated.dat'

    #Setting up for UQPCE
    (
        var_basis, norm_sq, resampled_var_basis,
        aleatory_cnt, epistemic_cnt, resp_cnt, order, variables,
        sig, run_matrix
    ) = interface.initialize(input_file, matrix_file)
    
    #Problem definition
    p = om.Problem()

    #Add subsystems
    p.model.add_subsystem('prop', Propulsion(vec_size=resp_cnt), 
                        promotes_inputs= ['SFC_tech', ('V_cruise', 'V'), 'SFC_ref', 'eta_base', 'kv_base', 'V_ref', 'delta_eta', 'delta_kv'], 
                        promotes_outputs= ['SFC'])
            
    p.model.add_subsystem('engine_weight', EngineWeight(vec_size=resp_cnt), 
                        promotes_inputs= ['SFC_tech', 'm_eng_ref', 'alpha_base', 'delta_alpha'], 
                        promotes_outputs= ['m_engine'])

    p.model.add_subsystem('aerostruct', AeroStruct(vec_size=resp_cnt), promotes=['*'])

    p.model.add_subsystem('DOC', DOC(vec_size=resp_cnt),
                        promotes_inputs=['SFC_tech', ('V_cruise', 'V'), ('R', 'R_comp'), 'm_fuel', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base', 'N_pax', 'delta_Cf', 'delta_beta'],
                        promotes_outputs=['DOC', 'Dpm'])
    
    #Adding UQPCE group
    p.model.add_subsystem(
        'UQPCE',
        UQPCEGroup(
            significance=sig, var_basis=var_basis, norm_sq=norm_sq, 
            resampled_var_basis=resampled_var_basis, tail='both',
            epistemic_cnt=epistemic_cnt, aleatory_cnt=aleatory_cnt,
            uncert_list=['Dpm'], tanh_omega=1e-3
        ),
        promotes_inputs=['Dpm'], 
        promotes_outputs=['Dpm:ci_lower', 'Dpm:ci_upper', 'Dpm:mean', 'Dpm:mean_plus_var']
    )    

    #Setting model input defaults
    p.model.set_input_defaults('AR', val=9.35)
    p.model.set_input_defaults('V', units='m/s', val=230.)
    p.model.set_input_defaults('S', units='m**2', val=125.)
    p.model.set_input_defaults('V_ref', val=230., units='m/s')

    #Setup optimizer
    p.driver = om.ScipyOptimizeDriver()
    p.driver.options['optimizer'] = 'SLSQP'
    # p.driver.options['tol'] = 1e-8

    #Set design variables, constraints, and objectives
    p.model.add_design_var('S', units='m**2', lower=0.)
    p.model.add_design_var('V', units='m/s', lower=0.)
    p.model.add_design_var('AR', lower=0.)
    p.model.add_design_var('SFC_tech', lower=-1.0, upper=1.0)

    p.model.add_constraint('CL', lower=0.0, upper=1.0) #CHANGE UPPER BOUND TO CL_MAX (STALL)

    p.model.add_objective('Dpm:mean')

    p.model.approx_totals()

    #PROBLEM SETUP
    p.setup(force_alloc_complex=True)
    interface.set_vals(p, variables, run_matrix)

    #Set values of parameters, design variables, state variables, and constants
    p.set_val('R_target', np.full(resp_cnt, 5740.), units='km')
    p.set_val('N_pax', 162.)
    p.set_val('m_payload', 16200., units='kg')
    p.set_val('SFC_ref', 1.6e-4, units='1/s')
    p.set_val('S_0', 124.6, units='m**2')
    p.set_val('V_ref', 235., units='m/s')
    p.set_val('m_fuse', 14000., units='kg')
    p.set_val('C_D0_base', 0.022)
    p.set_val('ks_base', 3.0e-5, units='1/m**2')
    p.set_val('e_base', 0.8)
    p.set_val('eta_base', 0.15)
    p.set_val('kv_base', 20.)
    p.set_val('kw_base', 95.)
    p.set_val('fsys_base', 0.09)
    p.set_val('p_base', 4.0)
    p.set_val('alpha_base', 0.2)
    p.set_val('beta_base', -0.25)
    p.set_val('Cf_base', 0.8, units='USD/kg')
    p.set_val('m_eng_ref', 5200., units='kg')
    p.set_val('C_time', 2000., units='USD/h') # 2000 USD/hr
    p.set_val('k_acq', 0.0001)
    p.set_val('C_eng_ref', 2.0e7, units='USD')

    p.set_val('S', 125., units='m**2')
    p.set_val('AR', 9.45)
    p.set_val('V', 230., units='m/s')
    p.set_val('SFC_tech', 0.)

    p.set_val('m_fuel', np.full(resp_cnt, 18000.), units='kg')

    p.set_val('rho', 1.225, units='kg/m**3') #.038
    p.set_val('g', 9.81, units='m/s**2')

    #PROBLEM SOLVE
    # p.set_solver_print(level=0)
    # p.run_driver()
    p.run_model()
    interface.analysis(p, 'Dpm', 'input.yaml', 'run_matrix_generated.dat')
    # om.n2(p)

    # partial_data = p.check_partials(out_stream=None, method='cs')
    # assert_check_partials(partial_data, atol=1e-12, rtol=1e-12)

    print(p.get_val('Dpm:mean'))
    # print(p.get_val('DOC'))
    print(p.get_val('AR'))
    print(p.get_val('V'))
    print(p.get_val('S'))
    print(p.get_val('SFC_tech'))