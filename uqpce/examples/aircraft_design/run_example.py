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
                           promotes_inputs= ['S', 'AR', ('V', 'V_cruise'), 'rho', 'g', 'C_D0_base', 'ks_base', 'e_base', 'S_0', 'm_total', 'delta_CD0', 'delta_ks', 'delta_e'], 
                           promotes_outputs= ['LD', 'CL'])    
    
        self.add_subsystem('mass', Weights_Struct(vec_size=vec_size), 
                           promotes_inputs= ['S', 'AR', 'V_cruise', 'm_engine', 'm_total', 'm_fuse', 'kw_base', 'fsys_base', 'p_base', 'V_ref', 'delta_kw', 'delta_fsys', 'delta_p'], 
                           promotes_outputs= ['m_empty'])
        
        self.add_subsystem('total_mass', TotalMassComp(vec_size=vec_size), 
                           promotes_inputs= ['m_empty', 'm_fuel', 'm_payload'], 
                           promotes_outputs= ['m_total'])
        
        self.add_subsystem('range', BreguetRangeComp(vec_size=vec_size), 
                           promotes_inputs= ['LD', 'SFC', ('V', 'V_cruise'), 'm_total', 'm_fuel'], 
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

from fixed import parameters    # Import fixed parameters file
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
                        promotes_inputs= ['SFC_tech', 'V_cruise', 'SFC_ref', 'eta_base', 'kv_base', 'V_ref', 'delta_eta', 'delta_kv'], 
                        promotes_outputs= ['SFC'])
            
    p.model.add_subsystem('engine_weight', EngineWeight(vec_size=resp_cnt), 
                        promotes_inputs= ['SFC_tech', 'm_eng_ref', 'alpha_base', 'delta_alpha'], 
                        promotes_outputs= ['m_engine'])

    p.model.add_subsystem('aerostruct', AeroStruct(vec_size=resp_cnt), promotes=['*'])

    p.model.add_subsystem('DOC', DOC(vec_size=resp_cnt),
                        promotes_inputs=['SFC_tech', 'V_cruise', ('R', 'R_comp'), 'm_fuel', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base', 'N_pax', 'delta_Cf', 'delta_beta'],
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
    p.model.set_input_defaults('V_cruise', units='m/s', val=230.)
    p.model.set_input_defaults('S', units='m**2', val=125.)
    p.model.set_input_defaults('V_ref', val=230., units='m/s')

    #Setup optimizer
    p.driver = om.ScipyOptimizeDriver()
    p.driver.options['optimizer'] = 'SLSQP'
    # p.driver.options['tol'] = 1e-8

    #Set design variables, constraints, and objectives
    p.model.add_design_var('S', units='m**2', lower=0.)
    p.model.add_design_var('V_cruise', units='m/s', lower=0.)
    p.model.add_design_var('AR', lower=0.)
    p.model.add_design_var('SFC_tech', lower=-1.0, upper=1.0)

    p.model.add_constraint('CL', lower=0.0, upper=1.0) #CHANGE UPPER BOUND TO CL_MAX (STALL)

    p.model.add_objective('Dpm:mean')

    p.model.approx_totals()

    #PROBLEM SETUP
    p.setup(force_alloc_complex=True)
    interface.set_vals(p, variables, run_matrix)

    #Set values of parameters, design variables, state variables, and constants
    p.set_val('R_target', np.full(resp_cnt, parameters['R_target']), units='m')
    p.set_val('N_pax', parameters['N_pax'])
    p.set_val('SFC_ref', parameters['SFC_ref'], units='1/s')
    p.set_val('V_ref', parameters['V_ref'], units='m/s')
    p.set_val('S_0', parameters['S_naught'], units='m**2')
    p.set_val('C_D0_base', parameters['CD0_base'])
    p.set_val('e_base', parameters['e_oswald_base'])

    p.set_val('fsys_base', parameters['fsys_base'])
    p.set_val('kw_base', parameters['kw_base'])
    p.set_val('p_base', parameters['p_base']) 
    p.set_val('eta_base', parameters['eta_base'])
    p.set_val('kv_base', parameters['kv_base'])
    p.set_val('alpha_base', parameters['alpha_base'])
    p.set_val('beta_base', parameters['beta_base'])
    p.set_val('ks_base', parameters['ks_base'], units='1/m**2')

    p.set_val('m_fuse', parameters['m_fuse'], units='kg')    
    p.set_val('m_payload', parameters['m_payload_design'], units='kg')
    p.set_val('m_eng_ref', parameters['m_eng_ref'], units='kg')

    p.set_val('m_fuel', np.full(resp_cnt, 18000.), units='kg') #Initial guess for fuel mass

    p.set_val('Cf_base', parameters['Cf_base'], units='USD/kg')
    p.set_val('C_time', parameters['C_time'], units='USD/h') # 2000 USD/hr
    p.set_val('k_acq', parameters['k_acq'])
    p.set_val('C_eng_ref', parameters['C_eng_ref'], units='USD')

    p.set_val('S', parameters['S'], units='m**2')
    p.set_val('AR', parameters['AR'])
    p.set_val('V_cruise', parameters['V'], units='m/s')
    p.set_val('SFC_tech', parameters['SFC_tech'])

    p.set_val('rho', 1.225, units='kg/m**3') #.038?
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
    print(p.get_val('V_cruise'))
    print(p.get_val('S'))
    print(p.get_val('SFC_tech'))