import openmdao.api as om
import numpy as np
import matplotlib.pyplot as plt
import os
from omjlcomps import JuliaExplicitComp
import juliacall; jl = juliacall.newmodule("Julia")

from disciplines.BreguetRange import BreguetRangeComp
from disciplines.aero import AeroComp
from disciplines.total_mass_comp import TotalMassComp
from disciplines.propulsion import PropulsionComp
from disciplines.weight import WeightsComp, EngineWeightComp

# from initialize_Julia import initialize
from organize import configure_subsystems, initialize
from fixed import parameters
from helpers import get_values

current_dir = os.path.dirname(os.path.abspath(__file__))
jl.include(os.path.join(current_dir, 'disciplines_Julia', 'propulsion.jl'))
jl.include(os.path.join(current_dir, 'disciplines_Julia', 'DOC.jl'))
jl.include(os.path.join(current_dir, 'disciplines_Julia', 'Dpm.jl'))
jl.include(os.path.join(current_dir, 'disciplines_Julia', 'engine.jl'))
jl.include(os.path.join(current_dir, 'disciplines_Julia', 'total_mass.jl'))

class CoupledDisciplines(om.Group):

    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        vector_size = self.options['vec_size']
        total_mass_comp = JuliaExplicitComp(jlcomp=jl.get_total_mass_ad(vector_size))

         ###Aerodynamics Component#################################
        self.add_subsystem(
            'Aero', AeroComp(vec_size=vector_size),
            promotes_inputs=['S', 'AR', 'V_cruise', 'rho', 'g', 'C_D0_base', 'ks_base', 'e_base', 'S_0', 'm_total', 'delta_CD0', 'delta_ks', 'delta_e'], 
            promotes_outputs=['CL','LD','WL']
        )
        #^######################################################^#

        ###Structural Weight Component############################
        self.add_subsystem(
            'Weight', WeightsComp(vec_size=vector_size),
            promotes_inputs=['S', 'AR', 'V_cruise', 'm_engine', 'm_total', 'm_fuse', 'kw_base', 'fsys_base', 'p_base', 'V_ref', 'delta_kw', 'delta_fsys', 'delta_p'],
            promotes_outputs=['m_empty']
        )
        #^######################################################^#

        ###Total Mass Component###################################
        self.add_subsystem(
            'Mass', total_mass_comp,
            promotes_inputs=['m_empty', 'm_fuel', 'm_payload'],
            promotes_outputs=['m_total']
        )
        #^######################################################^#

        ###Breguet Range Component################################
        self.add_subsystem(
            'Range', BreguetRangeComp(vec_size=vector_size),
            promotes_inputs=['LD', 'SFC', 'V_cruise', 'm_total', 'm_fuel'],
            promotes_outputs=['R']
        )
        #^######################################################^#

        ###Range Residual#########################################
        Balance = om.BalanceComp()
        
        Balance.add_balance(
            name='m_fuel', val=np.ones(vector_size)*16000,
            units='kg', lower=1000.0, upper=50000.0,
            lhs_name='R', rhs_name='R_target',
            rhs_val=parameters['R_target'],
            eq_units='m', ref=16000.0, res_ref=1.0e6,
        )
        
        self.add_subsystem('Balance', Balance,
                           promotes_inputs=['R', 'R_target'],
                           promotes_outputs=['m_fuel']
        )
        #^######################################################^#
        
        ###Residual Solver Options################################
        newton = self.nonlinear_solver = om.NewtonSolver(solve_subsystems=True)
        self.nonlinear_solver.options['iprint'] = 2
        self.nonlinear_solver.options['maxiter'] = 500
        self.nonlinear_solver.options['atol'] = 1e-5
        self.nonlinear_solver.options['rtol'] = 1e-3

        line_search = newton.linesearch = om.ArmijoGoldsteinLS(bound_enforcement='vector')
        line_search.options['maxiter'] = 20
        line_search.options['print_bound_enforce'] = True
        self.linear_solver = om.DirectSolver()
        #^######################################################^#

class DOC(om.ExplicitComponent):

    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']

        #proposed design variables
        self.add_input('SFC_tech', units="unitless")
        self.add_input('V_cruise', units='m/s')
        
        #model variable (output from other component)
        self.add_input('R', units='m', shape=(n,))
        self.add_input('m_fuel', units='kg', shape=(n,)) 

        #uncertain parameters
        self.add_input('delta_Cf', val=np.ones(n), units="unitless", shape=(n,))
        self.add_input('delta_beta', val=np.ones(n), units="unitless", shape=(n,))

        #tuning parameters
        self.add_input('Cf_base', units='USD/kg')
        self.add_input('beta_base', units="unitless")
        
        #constant parameters
        self.add_input('C_time', val=parameters['C_time'], units='USD/s')
        self.add_input('k_acq', val=parameters['k_acq'], units="unitless")
        self.add_input('C_eng_ref', val=parameters['C_eng_ref'], units='USD')

        #outputs
        self.add_output('DOC', units='USD',shape=(n,))
       
    def setup_partials(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.declare_partials('DOC', ['V_cruise', 'SFC_tech', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base'])
        self.declare_partials('DOC', ['R', 'm_fuel', 'delta_Cf', 'delta_beta'], rows=arange, cols=arange)

    def compute(self, inputs, outputs):
 
        SFC_tech = inputs['SFC_tech']
        V_cruise = inputs['V_cruise']
        Cf_base = inputs['Cf_base']
        m_fuel = inputs['m_fuel']
        C_time = inputs['C_time']
        R = inputs['R']
        k_acq = inputs['k_acq']
        C_eng_ref = inputs['C_eng_ref']
        beta_base = inputs['beta_base']
        delta_beta = inputs['delta_beta']
        delta_Cf = inputs['delta_Cf']

        outputs['DOC'] = DOC = Cf_base * delta_Cf * m_fuel + C_time * (R/V_cruise) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
        
    def compute_partials(self, inputs, partials):
        SFC_tech = inputs['SFC_tech']
        V = inputs['V_cruise']
        Cf_base = inputs['Cf_base']
        m_fuel = inputs['m_fuel']
        C_time = inputs['C_time']
        R = inputs['R']
        k_acq = inputs['k_acq']
        C_eng_ref = inputs['C_eng_ref']
        beta_base = inputs['beta_base']
        delta_Cf = inputs['delta_Cf']
        delta_beta = inputs['delta_beta']

        # DOC = Cf_base * delta_Cf * m_fuel + C_time * (R/V) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)

        partials['DOC', 'm_fuel'] = Cf_base * delta_Cf
        partials['DOC', 'R'] = C_time / V
        partials['DOC', 'V_cruise'] = -C_time * (R / V**2)
        partials['DOC', 'SFC_tech'] = k_acq * C_eng_ref * (beta_base * delta_beta)

        partials['DOC', 'Cf_base'] = delta_Cf * m_fuel
        partials['DOC', 'C_time'] = R / V
        partials['DOC', 'k_acq'] = C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
        partials['DOC', 'C_eng_ref'] = k_acq * (1 + beta_base * delta_beta * SFC_tech)
        partials['DOC', 'beta_base'] = (k_acq * C_eng_ref) * (delta_beta * SFC_tech)

        partials['DOC', 'delta_Cf'] = Cf_base * m_fuel
        partials['DOC', 'delta_beta'] = (k_acq * C_eng_ref) * (beta_base * SFC_tech)

class Dpm(om.ExplicitComponent):

    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']

        #proposed design variables
        #n/a

        #model variable (output from other component)
        self.add_input('DOC', units='USD', shape=(n,))
        self.add_input('R', units='km', shape=(n,))

        #uncertain parameters
        #n/a

        #tuning parameters
        #n/a

        #constant parameters
        self.add_input('N_pax', val=parameters['N_pax'], units='unitless')

        #outputs
        self.add_output('Dpm', shape=(n,))

    def setup_partials(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.declare_partials('Dpm', ['N_pax'])
        self.declare_partials('Dpm', ['R', 'DOC'], rows=arange, cols=arange)

    def compute(self, inputs, outputs):

        N_pax = inputs['N_pax']
        DOC = inputs['DOC']
        R = inputs['R']

        outputs['Dpm'] = DOC / (N_pax * R)
    
    def compute_partials(self, inputs, partials):
        N_pax = inputs['N_pax']
        DOC = inputs['DOC']
        R = inputs['R']

        partials['Dpm', 'R'] = -(DOC / (N_pax * R**2))
        partials['Dpm', 'N_pax'] = -(DOC / (N_pax**2 * R))
        partials['Dpm', 'DOC'] = 1 / (N_pax * R)
        
class CL_constraint(om.ExplicitComponent):
    
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.add_input('CL', shape=(n,))

        self.add_input('CL_target', val=0.53)

        self.add_output('CL_constraint', shape=(n,))

        # should be identity matrix
        self.declare_partials('CL_constraint', 'CL', rows=arange, cols=arange)

    def compute(self, inputs, outputs):

        CL = inputs['CL']
        CL_target = inputs['CL_target']

        outputs['CL_constraint'] = CL_target - CL

    def compute_partials(self, inputs, partials):

        partials['CL_constraint', 'CL'] = -1

class WingLoad_constraint(om.ExplicitComponent):
    
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.add_input('WL', shape=(n,))

        self.add_input('WL_target',val=5905.0)

        self.add_output('WL_constraint', shape=(n,))

        # should be identity matrix
        self.declare_partials('WL_constraint', 'WL', rows=arange, cols=arange)

    def compute(self, inputs, outputs):

        WL = inputs['WL']
        WL_target = inputs['WL_target']

        outputs['WL_constraint'] = WL_target - WL

    def compute_partials(self, inputs, partials):

        partials['WL_constraint', 'WL'] = 1

from uqpce.mdao.uqpcegroup import UQPCEGroup
from uqpce.mdao import interface

def configure_subsystems(prob, vector_size=1):
    prop_comp = JuliaExplicitComp(jlcomp=jl.get_prop_ad(vector_size))
    DOC_comp = JuliaExplicitComp(jlcomp=jl.get_DOC_ad(vector_size))
    Dpm_comp = JuliaExplicitComp(jlcomp=jl.get_Dpm_ad(vector_size))
    engine_comp = JuliaExplicitComp(jlcomp=jl.get_engine_ad(vector_size))
    # prob.model.add_subsystem(
    #     'Prop', Propulsion(vec_size=vector_size),
    #     promotes_inputs=['SFC_tech','V_cruise', 'SFC_ref', 'eta_base', 'kv_base', 'V_ref', 'delta_eta', 'delta_kv'],
    #     promotes_outputs=['SFC']
    # )

    #Julia Component--
    prob.model.add_subsystem(
        'Prop', prop_comp,
        promotes_inputs=['SFC_tech', 'V_cruise', 'SFC_ref', 'eta_base', 'kv_base', 'V_ref', 'delta_eta', 'delta_kv'],
        promotes_outputs=['SFC']
    )
    #---

    prob.model.add_subsystem(
        'engine_weight', engine_comp, 
        promotes_inputs=['SFC_tech', 'm_eng_ref', 'alpha_base', 'delta_alpha'], 
        promotes_outputs=['m_engine']
    )
    
    prob.model.add_subsystem(
        'AeroStruct', CoupledDisciplines(vec_size=vector_size), 
        promotes=['*']
    )

   # prob.model.add_subsystem(
   #     'WingLoad_constraint', WingLoad_constraint(vec_size=vector_size), 
   #     promotes_inputs=['WL'], 
   #     promotes_outputs=['WL_constraint']
   # )

    prob.model.add_subsystem(
        'LiftCoeff_constraint', CL_constraint(vec_size=vector_size), 
        promotes_inputs=['CL'], 
        promotes_outputs=['CL_constraint']
    )

    prob.model.add_subsystem(
        'DOC_objective', DOC_comp, 
        promotes_inputs=['SFC_tech', 'V_cruise', 'R', 'm_fuel', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base', 'delta_Cf', 'delta_beta'], 
        promotes_outputs=['DOC']
    )

    prob.model.add_subsystem(
        'DPM_objective', Dpm_comp, 
        promotes_inputs=['DOC', 'R', 'N_pax'], 
        promotes_outputs=['Dpm']
    )

def main():
    """
    This script will run two dterministic optimizations:
        1) C_L constrained problem
        2) Wing Loading Constrained problem
    
    Then, the optimal values from each run will be fed into uqpce
    To generate probability density plots of the model responses 
    at the two dtermninistic optima.

    Finally, the script will perform 6 optimzations under uncertainty:
        1) mean C_L constrained problem
        2) lower C_L confidence interval constrained problem
        3) upper C_L confidence interval constrained problem
        4) mean Wing_Loading constrained problem
        2) lower  Wing_Loading confidence interval constrained problem
        3) upper  Wing_Loading confidence interval constrained problem

    In the end, we should be rewarded with 2 + 6 = 8 sets of plots...
    """

    #~~~~~Deterministic Optimizations~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    determ_prob = om.Problem()

    configure_subsystems(determ_prob)

    determ_prob.model.set_input_defaults('S', val=124.6, units='m**2')
    determ_prob.model.set_input_defaults('AR', val=9.45)
    determ_prob.model.set_input_defaults('V_cruise', val=235.0, units='m/s')
    determ_prob.model.set_input_defaults('SFC_tech', val=0.0)
    
    # Optimizer
    determ_prob.driver = om.ScipyOptimizeDriver()
    determ_prob.driver.options['optimizer'] = 'SLSQP'
    determ_prob.driver.options['maxiter'] = 1000
    determ_prob.driver.options['tol'] = 1e-12
    determ_prob.driver.options['disp'] = True

    # Declare Design variables
    determ_prob.model.add_design_var('S', lower=100.0, upper=180.0, ref=124.6)
    determ_prob.model.add_design_var('AR', lower=7.0, upper=50.0, ref=9.45)
    determ_prob.model.add_design_var('V_cruise', lower=200, upper=260, ref=1)
    determ_prob.model.add_design_var('SFC_tech', lower=-1, upper=1, ref=1)

    # Declare Objective Function
    determ_prob.model.add_objective('DOC', ref=1.0e4)
    
    determ_prob.model.add_constraint('m_fuel', lower=1000.0, upper=50000.0, ref=16000.0)
    determ_prob.model.add_constraint('CL_constraint', lower=0, upper = 0.53, ref=0.1)
    #determ_prob.model.add_constraint('WL_constraint', lower=-5905, upper = 5905, ref=0.1)

    determ_prob.setup()
    initialize(determ_prob, parameters)

    determ_prob.run_driver()
    #display_results(determ_prob)

    S_opt = determ_prob.get_val('S')
    AR_opt = determ_prob.get_val('AR')
    V_cruise_opt = determ_prob.get_val('V_cruise')
    SFC_tech_opt = determ_prob.get_val('SFC_tech')
    print(AR_opt)

    optimal = {
       'V_cruise': V_cruise_opt,
       'AR': AR_opt,
       'S': S_opt,
       'SFC_tech': SFC_tech_opt
    }

#     #---------------------------------------------------------------------------
#     #                               Input Files
#     #---------------------------------------------------------------------------

#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     relative_yaml = 'input.yaml'
#     relative_matrix = 'run_matrix_generated.dat'
#     input_file = os.path.join(script_dir, relative_yaml)
#     matrix_file  = os.path.join(script_dir, relative_matrix)

#     #---------------------------------------------------------------------------
#     #                   Setting up for UQPCE and design under uncertainty
#     #---------------------------------------------------------------------------

#     (
#         var_basis, norm_sq, resampled_var_basis, 
#         aleatory_cnt, epistemic_cnt, resp_cnt, order, variables, 
#         sig, run_matrix
#     ) = interface.initialize(input_file, matrix_file)
    
#     uncertain_prob = om.Problem()

#     uncertain_prob.driver = om.ScipyOptimizeDriver()
#     uncertain_prob.driver.options['optimizer'] = 'SLSQP'
#     uncertain_prob.driver.options['maxiter'] = 1000
#     uncertain_prob.driver.options['tol'] = 1e-10
#     uncertain_prob.driver.options['disp'] = True

#     uncertain_prob.driver.options['debug_print'] = [
#     'desvars',
#     'objs',
#     'nl_cons',
#     ]

#     configure_subsystems(uncertain_prob,vector_size=resp_cnt)

#     uncertain_prob.model.set_input_defaults('S', val=124.6, units='m**2')
#     uncertain_prob.model.set_input_defaults('AR', val=9.45)
#     uncertain_prob.model.set_input_defaults('V_cruise', val=235.0, units='m/s')
#     uncertain_prob.model.set_input_defaults('SFC_tech', val=0.0)

#     #---------------------------------------------------------------------------
#     #                   Add UQPCE Group to Problem
#     #---------------------------------------------------------------------------

#     probailistic_DOC_list = ['DOC:resampled_responses','DOC:ci_lower',
#                              'DOC:ci_upper','DOC:mean','DOC:mean_plus_var']
    
#     probailistic_Dpm_list = ['Dpm:resampled_responses','Dpm:ci_lower',
#                              'Dpm:ci_upper','Dpm:mean','Dpm:mean_plus_var']
    
#     probailistic_m_fuel_list = ['m_fuel:resampled_responses','m_fuel:ci_lower',
#                                 'm_fuel:ci_upper','m_fuel:mean','m_fuel:mean_plus_var',]
    
#     probailistic_m_empty_list = ['m_empty:resampled_responses','m_empty:ci_lower',
#                                  'm_empty:ci_upper', 'm_empty:mean','m_empty:mean_plus_var',]
    
#     probailistic_m_engine_list = ['m_engine:resampled_responses','m_engine:ci_lower',
#                                   'm_engine:ci_upper','m_engine:mean','m_engine:mean_plus_var',]
    
#     probailistic_m_total_list = ['m_total:resampled_responses','m_total:ci_lower',
#                                  'm_total:ci_upper','m_total:mean','m_total:mean_plus_var',]
    
#     probailistic_CL_list = ['CL:resampled_responses','CL:ci_lower',
#                             'CL:ci_upper','CL:mean','CL:mean_plus_var']

#     probailistic_CD_list = ['CD:resampled_responses','CD:ci_lower',
#                             'CD:ci_upper','CD:mean','CD:mean_plus_var']
    
#     probailistic_SFC_list = ['SFC:resampled_responses','SFC:ci_lower',
#                              'SFC:ci_upper','SFC:mean','SFC:mean_plus_var',]
    
#     probailistic_CL_constr_list = ['CL_constraint:resampled_responses',
#                                    'CL_constraint:ci_lower',
#                                    'CL_constraint:ci_upper',
#                                    'CL_constraint:mean',
#                                    'CL_constraint:mean_plus_var']
    
#   #  probailistic_WL_constr_list = ['WL_constraint:resampled_responses',
#   #                                 'WL_constraint:ci_lower',
#   #                                 'WL_constraint:ci_upper',
#   #                                 'WL_constraint:mean',
#   #                                 'WL_constraint:mean_plus_var']

#     probailistic_output_list = (probailistic_DOC_list +
#                                 probailistic_Dpm_list +
#                                 probailistic_m_fuel_list +
#                                 probailistic_m_empty_list +
#                                 probailistic_m_engine_list +
#                                 probailistic_m_total_list +
#                                 probailistic_CL_list +
#                                 probailistic_CD_list +
#                                 probailistic_SFC_list +
#                                 probailistic_CL_constr_list )
#    #                             probailistic_WL_constr_list)

#     uncertain_prob.model.add_subsystem(
#         'UQPCE',
#         UQPCEGroup(
#             significance=sig,
#             var_basis=var_basis,
#             norm_sq=norm_sq,
#             resampled_var_basis=resampled_var_basis,
#             tail='both',
#             epistemic_cnt=epistemic_cnt,
#             aleatory_cnt=aleatory_cnt,
#             uncert_list=['DOC','Dpm', 'm_fuel','m_empty','m_engine','m_total','CL','CD','SFC','CL_constraint'],
#             tanh_omega=1e-3,
#             sample_ref0=[ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0,0.0,0.0,0.0],
#             sample_ref=[ 5.0e4, 0.01, 1000, 1000, 1000, 1000,0.1,0.1,0.0001,0.1],
#         ),
#         promotes_inputs=[ 'DOC','Dpm', 'm_fuel','m_empty','m_engine','m_total','CL','CD','SFC','CL_constraint'],
#         promotes_outputs= probailistic_output_list
#     )

#     # Declare Design variables
#     uncertain_prob.model.add_design_var('S', lower=100.0, upper=180.0, ref=124.6)
#     uncertain_prob.model.add_design_var('AR', lower=7.0, upper=50.0, ref=9.45)
#     uncertain_prob.model.add_design_var('V_cruise', lower=200, upper=260, ref=1)
#     uncertain_prob.model.add_design_var('SFC_tech', lower=-1, upper=1, ref=1)

#     # Declare Objective Function
#     uncertain_prob.model.add_objective('DOC:mean', ref=1.0e4)
    
#     uncertain_prob.model.add_constraint('m_fuel:mean', lower=1000.0, upper=50000.0, ref=16000.0)
#     uncertain_prob.model.add_constraint('CL_constraint:ci_lower',lower=0.0,upper=0.53, ref0=1, ref=2)
    
#     #same evvect as expected
#     #uncertain_prob.model.add_constraint('CL:mean',upper=0.53)
#     #uncertain_prob.model.add_constraint('CL_constraint:mean',equals=0.0)


#     uncertain_prob.setup()
#     initialize(uncertain_prob, optimal)
#     interface.set_vals(uncertain_prob,variables,run_matrix)

#     uncertain_prob.run_model()

#     print(uncertain_prob.get_val("AR"))

#     response = get_values(uncertain_prob, copybool=True)
 
#     initialize(uncertain_prob, optimal)

#     uncertain_prob.run_driver()

#     optimized = get_values(uncertain_prob)

#     print(uncertain_prob.get_val("AR"))

#     # plot_objective(response, optimized)

#     # plot_coefficients(response, optimized)
    
#     # plot_constraints(response,optimized)

#     # plot_mass(response,optimized)

#     # plot_sfc(response,optimized)

if __name__ == "__main__":
    main()