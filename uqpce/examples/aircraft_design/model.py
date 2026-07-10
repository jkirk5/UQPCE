import openmdao.api as om
import numpy as np
import matplotlib.pyplot as plt
#helpers
from aero import distribute_input
#components
from aero import AeroDiscipline
from BreguetRangeComp import BreguetRangeComp
from propAndCost import Propulsion
from propAndCost import EngineWeight
from propAndCost import DOC
from propAndCost import Dpm
from WeightsComp import Weights_Struct
from total_mass_comp import TotalMassComp

from helpers import *
from sweepers import *

#corresponds to original main script/func
class CoupledGroup(om.Group):

    def setup(self):
        self.add_subsystem('aero', AeroDiscipline(vec_size=1), 
                           promotes_inputs=['S', 'AR', ('V', 'V_cruise'), 'rho', 'g', 'C_D0_base', 'ks_base', 'e_base', 'S_0', 'm_total', 'delta_CD0', 'delta_ks', 'delta_e'], 
                           promotes_outputs=['LD', 'CL', 'CD'])    
    
        self.add_subsystem('mass', Weights_Struct(vec_size=1), 
                           promotes_inputs=['S', 'AR', ('V', 'V_cruise'), 'm_engine', 'm_total', 'm_fuse', 'kw_base', 'fsys_base', 'p_base', 'V_ref', 'delta_kw', 'delta_fsys', 'delta_p'], 
                           promotes_outputs=['m_empty'])
        
        self.add_subsystem('total_mass', TotalMassComp(vec_size=1), 
                           promotes_inputs=['m_empty', 'm_fuel', 'm_payload'], 
                           promotes_outputs=['m_total'])
        
        self.add_subsystem('range', BreguetRangeComp(vec_size=1), 
                           promotes_inputs=['LD', 'SFC', ('V', 'V_cruise'), 'm_total', 'm_fuel'], 
                           promotes_outputs=['R'])

        Balance = om.BalanceComp()
        Balance.add_balance(
            name='m_fuel',
            val=16000.0,
            units='kg',
            lower=1000.0,
            upper=50000.0,
            lhs_name='R',
            rhs_name='R_target',
            eq_units='m',
            ref=16000.0,
            res_ref=1.0e6,
            )
        self.add_subsystem('Balance', Balance, 
                           promotes_inputs=['R', 'R_target'],
                           promotes_outputs=['m_fuel'])

        self.nonlinear_solver = om.NewtonSolver(solve_subsystems=True)
        self.nonlinear_solver.options['iprint'] = 2
        self.nonlinear_solver.options['maxiter'] = 500
        self.nonlinear_solver.options['atol'] = 1e-12
        self.nonlinear_solver.options['rtol'] = 1e-12

        self.nonlinear_solver.linesearch = om.BoundsEnforceLS()
        self.nonlinear_solver.linesearch.options['bound_enforcement'] = 'scalar'

        self.linear_solver = om.DirectSolver()

#constraint
#corresponds to uqpce main script/func
class AeroConst(om.ExplicitComponent):
    """
    Component containing Constraint for component 1
    Needed now because the constraint must act across entire vector.
    It would probably work otherwise, but this is more clear
    """

    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)
    
    def setup(self):
        n = self.options['vec_size']
        self.add_input('CL', shape=(n,))
        self.add_output('CL_constraint', shape=(n,))


    def setup_partials(self):
        n = self.options['vec_size']
        idx = np.arange(n)
        self.declare_partials('CL_constraint','CL',rows=idx,cols=idx)
    
    def compute(self, inputs, outputs):
        CL = inputs['CL']
        CL_target = 0.53
        outputs['CL_constraint'] = CL_target - CL



    def compute_partials(self, inputs, partials):
        partials['CL_constraint','CL'] = -1

#corresponds to uqpce main script/func
class ExampleMDA(om.Group):

    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)
    
    def setup(self):
        n = self.options['vec_size']
        self.add_subsystem('aero', AeroDiscipline(vec_size=n), 
                           promotes_inputs=['S', 'AR', ('V', 'V_cruise'), 'rho', 'g', 'C_D0_base', 'ks_base', 'e_base', 'S_0', 'm_total', 'delta_CD0', 'delta_ks', 'delta_e'], 
                           promotes_outputs=['LD', 'CL', 'CD'])    
    
        self.add_subsystem('mass', Weights_Struct(vec_size=n), 
                           promotes_inputs=['S', 'AR', ('V', 'V_cruise'), 'm_engine', 'm_total', 'm_fuse', 'kw_base', 'fsys_base', 'p_base', 'V_ref', 'delta_kw', 'delta_fsys', 'delta_p'], 
                           promotes_outputs=['m_empty'])
        
        self.add_subsystem('total_mass', TotalMassComp(vec_size=n), 
                           promotes_inputs=['m_empty', 'm_fuel', 'm_payload'], 
                           promotes_outputs=['m_total'])
        
        self.add_subsystem('range', BreguetRangeComp(vec_size=n), 
                           promotes_inputs=['LD', 'SFC', ('V', 'V_cruise'), 'm_total', 'm_fuel'], 
                           promotes_outputs=['R'])
        
        Balance = om.BalanceComp()
        Balance.add_balance(
            name='m_fuel',
            val=9000.0 * np.ones(n),
            units='kg',
            lower=1000.0,
            upper=50000.0,
            lhs_name='R',
            rhs_name='R_target',
            eq_units='m',
            ref=16000.0,
            res_ref=1.0e6,
            )
        self.add_subsystem('Balance', Balance, 
                           promotes_inputs=['R', 'R_target'],
                           promotes_outputs=['m_fuel'])

        self.nonlinear_solver = om.NewtonSolver(solve_subsystems=True)
        self.nonlinear_solver.options['iprint'] = 2
        self.nonlinear_solver.options['maxiter'] = 500
        self.nonlinear_solver.options['atol'] = 1e-10
        self.nonlinear_solver.options['rtol'] = 1e-10

        self.nonlinear_solver.linesearch = om.BoundsEnforceLS()
        self.nonlinear_solver.linesearch.options['bound_enforcement'] = 'scalar'

        self.linear_solver = om.DirectSolver()

from uqpce.mdao.uqpcegroup import UQPCEGroup
from uqpce.mdao import interface
import os
from fixed import optimal
def uqpce_main_script():
    #---------------------------------------------------------------------------
    #                               Input Files
    #---------------------------------------------------------------------------

    # script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = 'input.yaml'
    matrix_file = 'run_matrix_generated.dat'
    # input_file = os.path.join(script_dir, relative_yaml)
    # matrix_file  = os.path.join(script_dir, relative_matrix)

    #---------------------------------------------------------------------------
    #                   Setting up for UQPCE and design under uncertainty
    #---------------------------------------------------------------------------

    (
        var_basis, norm_sq, resampled_var_basis, 
        aleatory_cnt, epistemic_cnt, resp_cnt, order, variables, 
        sig, run_matrix
    ) = interface.initialize(input_file, matrix_file)
    
    prob = om.Problem()

    #---------------------------------------------------------------------------
    #                   Add Subsystems to Problem
    #---------------------------------------------------------------------------
    prob.model.add_subsystem('prop', Propulsion(vec_size=resp_cnt), 
                        promotes_inputs=['SFC_tech', ('V', 'V_cruise'), 'SFC_ref', 'eta_base', 'kv_base', 'V_ref', 'delta_eta', 'delta_kv'], 
                        promotes_outputs=['SFC'])
            
    prob.model.add_subsystem('engine_weight', EngineWeight(vec_size=resp_cnt), 
                    promotes_inputs=['SFC_tech', 'm_eng_ref', 'alpha_base', 'delta_alpha'], 
                    promotes_outputs=['m_engine'])
    
    prob.model.add_subsystem('MDA', ExampleMDA(vec_size=resp_cnt), 
                    promotes=['*']
    )

    # prob.model.add_subsystem(
    #     'CL_constraint', 
    #      AeroConst(vec_size=resp_cnt), 
    #      promotes_outputs=['CL_constraint']
    # )

    prob.model.add_subsystem('DOC', DOC(vec_size=resp_cnt),
                        promotes_inputs=['SFC_tech', 'V_cruise', 'R', 'm_fuel', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base', 'delta_Cf', 'delta_beta'],
                        promotes_outputs=['DOC'])
    
    prob.model.add_subsystem('DOC_pax_km', Dpm(vec_size=resp_cnt),
                    promotes_inputs=['DOC', 'N_pax', 'R'],
                    promotes_outputs=['Dpm'])

    #---------------------------------------------------------------------------
    #                   Add UQPCE Group to Problem
    #---------------------------------------------------------------------------
    prob.model.add_subsystem(
        'UQPCE',
        UQPCEGroup(
            significance=sig,
            var_basis=var_basis,
            norm_sq=norm_sq,
            resampled_var_basis=resampled_var_basis,
            tail='both',
            epistemic_cnt=epistemic_cnt,
            aleatory_cnt=aleatory_cnt,
            uncert_list=['DOC','Dpm'],
            tanh_omega=1e-3,
        ),
        promotes_inputs=['DOC', 'Dpm'],
        promotes_outputs=[
            'DOC:resampled_responses',
            'DOC:ci_lower',
            'DOC:ci_upper',
            'DOC:mean',
            'DOC:mean_plus_var',
            
            'Dpm:resampled_responses',
            'Dpm:ci_lower',
            'Dpm:ci_upper',
            'Dpm:mean',
            'Dpm:mean_plus_var',
        ]
    )

    #---------------------------------------------------------------------------
    #                   Setting up the OpenMDAO Problem
    #---------------------------------------------------------------------------
    prob.model.set_input_defaults('S', val=optimal['S'], units='m**2')
    prob.model.set_input_defaults('AR', val=optimal['AR'])
    prob.model.set_input_defaults('V_cruise', val=optimal['V'], units='m/s')
    prob.model.set_input_defaults('SFC_tech', val=optimal['SFC_tech'])

    prob.setup()
    interface.set_vals(prob, variables, run_matrix)
    
    initialize(prob)

    prob.run_model()

    print('Design Variable S ', prob.get_val('S'))
    print('Design Variable AR ', prob.get_val('AR'))
    print('Design Variable V ', prob.get_val('V_cruise'))
    print('Design Variable SFC_tech ', prob.get_val('SFC_tech'))

    #print(f'Constraint {CL_con}', prob.get_val(CL_con))
    #print(f'Objective {obj} is', prob.get_val(obj))

    #print('Fuel mass ', prob.get_val('m_fuel'))
    # print('Range ', prob.get_val('R'))
    print('DOC ', prob.get_val('DOC:mean'))
    #print('Dpm ', prob.get_val('Dpm'))

    print('CL', prob.get_val('CL'))
    # print('CD', prob.get_val('CD'))

    # plot_uqpce_pretty(prob)

    interface.analysis(prob, 'Dpm', 'input.yaml', 'run_matrix_generated.dat')
    # interface.analysis(prob, 'DOC', 'input.yaml', 'run_matrix_generated.dat')

def original_main_script():

    prob = om.Problem()
    prob.model.add_subsystem('prop', Propulsion(vec_size=1), 
                        promotes_inputs=['SFC_tech', ('V', 'V_cruise'), 'SFC_ref', 'eta_base', 'kv_base', 'V_ref', 'delta_eta', 'delta_kv'], 
                        promotes_outputs=['SFC'])
            
    prob.model.add_subsystem('engine_weight', EngineWeight(vec_size=1), 
                    promotes_inputs=['SFC_tech', 'm_eng_ref', 'alpha_base', 'delta_alpha'], 
                    promotes_outputs=['m_engine'])
    
    prob.model.add_subsystem('aircraft', CoupledGroup(), promotes=['*'])
    
    prob.model.add_subsystem('DOC', DOC(vec_size=1),
                        promotes_inputs=['SFC_tech', 'V_cruise', 'R', 'm_fuel', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base', 'delta_Cf', 'delta_beta'],
                        promotes_outputs=['DOC'])
    
    prob.model.add_subsystem('DOC_pax_km', Dpm(vec_size=1),
                    promotes_inputs=['DOC', 'N_pax', 'R'],
                    promotes_outputs=['Dpm'])
    
    # 737-800-ish baseline
    prob.model.set_input_defaults('S', val=124.6, units='m**2')       # m^2
    prob.model.set_input_defaults('AR', val=9.45)                     # -
    prob.model.set_input_defaults('V_cruise', val=235.0, units='m/s')        # m/s
    prob.model.set_input_defaults('SFC_tech', val=0.0)                # baseline technology
   
    # Optimizer
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'SLSQP'
    prob.driver.options['maxiter'] = 100
    prob.driver.options['tol'] = 1e-6
    prob.driver.options['disp'] = True

    # Declare Design Variables
    prob.model.add_design_var('S', lower=100.0, upper=180.0, ref=124.6, units='m**2')
    prob.model.add_design_var('AR', lower=7.0, upper=50.0, ref=9.45)
    prob.model.add_design_var('V_cruise', lower=200, upper=260, ref=1, units='m/s')
    prob.model.add_design_var('SFC_tech', lower=-1, upper=1, ref=1)

    # Declare Objective and Constraint Functions
    prob.model.add_objective('Dpm', ref=1.0e-1)
    prob.model.add_constraint('CL', lower=0.4, upper=0.53, ref=0.5)

    prob.setup()

    # Initial design points
    initialize_og(prob)

    prob.run_model()

    print('\n~~~~737-800 Design~~~~\n\n')
    print('S:', prob.get_val('S'))
    print('AR:', prob.get_val('AR'))
    print('V:', prob.get_val('V_cruise'))
    print('SFC_tech:', prob.get_val('SFC_tech'))

    print('737-800 DOC estimate [$/flight]:', prob.get_val('DOC'))

    prob.run_driver()

    # prob.check_totals(of=['Dpm'], wrt=['S', 'AR', 'SFC_tech','V_cruise'],
    #                  compact_print=True, method='fd')

    print('\n~~~~Optimized Design~~~~\n\n')
    print('S:', prob.get_val('S'))
    print('AR:', prob.get_val('AR'))
    print('V:', prob.get_val('V_cruise'))
    AR_temp = prob.get_val('AR')
    S_temp = prob.get_val('S')
    print('b', np.sqrt(AR_temp*S_temp))
    print('SFC_tech:', prob.get_val('SFC_tech'))

    print('\n~~~~Outputs~~~~\n\n')
    
    print('DOC [$/flight]:', prob.get_val('DOC'))
    print('DOC/pax*km [$/pax*km]:', prob.get_val('Dpm'))
    print('\nMASSES\n')
    print('m_total:', prob.get_val('m_total'))
    print('m_empty:', prob.get_val('m_empty'))
    print('m_fuel:', prob.get_val('m_fuel'))
    print('\n~~~~\n')
    print('Range [km]:', prob.get_val('R')/1000)
    print('\n~~~~\n')
    print('Lift to Drag ratio:', prob.get_val('LD'))
    print('Lift Coefficient:', prob.get_val('CL'))
    print('Drag Coefficient:',prob.get_val('CD'))
    print('\n~~~~\n')
    print('SFC:', prob.get_val('SFC'))
    print('Reference SFC:', parameters['SFC_ref'])

    # om.n2(prob)

def main():
    uqpce_main_script()
    # original_main_script()    
    
if __name__ == "__main__":
    main()
