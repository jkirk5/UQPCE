import openmdao.api as om
import numpy as np
import matplotlib.pyplot as plt
#helpers
from aero import distribute_input
#components
from aero import AeroDicipline
from BreguetRangeComp import BreguetRangeComp
from propAndCost import Propulsion
from propAndCost import EngineWeight
from WeightsComp import Weights_Struct
from total_mass_comp import TotalMassComp

from helpers import *
from sweepers import *

#corresponds to original main script/func
class CoupledGroup(om.Group):

    def setup(self):
        # 737-800-ish baseline
        self.set_input_defaults('S', val=124.6)       # m^2
        self.set_input_defaults('AR', val=9.45)       # -
        self.set_input_defaults('V', val=235.0)       # m/s
        self.set_input_defaults('SFC_tech', val=0.0)  # baseline technology

        self.add_subsystem('Prop', Propulsion(), promotes_inputs=['V', 'SFC_tech'])
        self.add_subsystem('Engine', EngineWeight(), promotes_inputs=['SFC_tech'])
        self.add_subsystem('Aero', AeroDicipline(), promotes_inputs=['S', 'AR', 'V'])
        self.add_subsystem('Weight', Weights_Struct(), promotes_inputs=['S', 'AR', 'V'])
        self.add_subsystem('Mass', TotalMassComp())
        self.add_subsystem('Range', BreguetRangeComp(), promotes_inputs=['V'])

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
        self.add_subsystem('Balance', Balance)

        
        self.add_subsystem('DOC', DOC(), promotes_inputs=['V', 'SFC_tech'])

        self.connect('Balance.m_fuel', 'Range.m_fuel')
        self.connect('Mass.m_total', 'Range.m_total')
        self.connect('Aero.LD', 'Range.LD')
        self.connect('Prop.SFC', 'Range.SFC')

        self.connect('Range.R', 'Balance.R')

        self.connect('Balance.m_fuel', 'Mass.m_fuel')
        self.connect('Weight.m_empty', 'Mass.m_empty')

        self.connect('Mass.m_total', 'Aero.m_total')

        self.connect('Engine.m_engine', 'Weight.m_engine')
        self.connect('Mass.m_total', 'Weight.m_total')

        self.connect('Range.R', 'DOC.R')
        self.connect('Balance.m_fuel', 'DOC.m_fuel')

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

#objective
#corresponds to uqpce main script/func
class DOC(om.ExplicitComponent):
    """
    Component for "DOCComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size',default=1,types=int)

    def setup(self):
        n = self.options['vec_size']

        #Parameters
        self.add_input('Cf_base', units='USD/kg')
        self.add_input('C_time', units='USD/s')
        self.add_input('k_acq')
        self.add_input('C_eng_ref', units='USD')
        self.add_input('beta_base')

        self.add_input('N_pax', desc="Number of passengers")

        #Global design variables
        self.add_input('SFC_tech', val=0., desc='SFC technology factor')
        self.add_input('V', units='m/s', desc='Cruise speed')

        #Local design variable
        self.add_input('R',shape=(n,), units='km', desc='Breguet range')
        
        #Solver state
        self.add_input('m_fuel',shape=(n,), units='kg', desc='Fuel mass') 

        #Uncertainties
        self.add_input('delta_Cf', val=1.0, shape=(n,))
        self.add_input('delta_beta', val=1.0, shape=(n,))

        #Output
        self.add_output('DOC', units='USD', desc="Direct operating cost", shape=(n,))

        self.add_output('Dpm', desc="DOC/pax*km", shape=(n,))

    def setup_partials(self):
        n = self.options['vec_size']
        idx = np.arange(n)

        self.declare_partials('DOC', ['V', 'SFC_tech', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base'])
        self.declare_partials('DOC', ['m_fuel', 'R','delta_Cf', 'delta_beta'], rows=idx, cols=idx)

        self.declare_partials('Dpm', ['V', 'SFC_tech', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base', 'N_pax'])
        self.declare_partials('Dpm', ['m_fuel', 'R','delta_Cf', 'delta_beta'], rows=idx, cols=idx)

    def compute(self, inputs, outputs):
        """
        DOC = Cf_base * delta_Cf * m_fuel + C_time * (R / V) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
        """

        SFC_tech = inputs['SFC_tech']
        V = inputs['V']
        Cf_base = inputs['Cf_base']
        m_fuel = inputs['m_fuel']
        C_time = inputs['C_time']
        R = inputs['R']
        k_acq = inputs['k_acq']
        C_eng_ref = inputs['C_eng_ref']
        beta_base = inputs['beta_base']
        delta_beta = inputs['delta_beta']
        delta_Cf = inputs['delta_Cf']

        N_pax = inputs['N_pax']

        outputs['DOC'] = DOC = Cf_base * delta_Cf * m_fuel + C_time * (R/V) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)

        outputs['Dpm'] = DOC / (N_pax * R)
    
    def compute_partials(self, inputs, partials):
        SFC_tech = inputs['SFC_tech']
        V = inputs['V']
        Cf_base = inputs['Cf_base']
        m_fuel = inputs['m_fuel']
        C_time = inputs['C_time']
        R = inputs['R']
        k_acq = inputs['k_acq']
        C_eng_ref = inputs['C_eng_ref']
        beta_base = inputs['beta_base']
        delta_Cf = inputs['delta_Cf']
        delta_beta = inputs['delta_beta']

        N_pax = inputs['N_pax']

        DOC = Cf_base * delta_Cf * m_fuel + C_time * (R/V) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)

        partials['DOC', 'm_fuel'] = Cf_base * delta_Cf
        partials['DOC', 'R'] = C_time / V
        partials['DOC', 'V'] = -C_time * (R / V**2)
        partials['DOC', 'SFC_tech'] = k_acq * C_eng_ref * (beta_base * delta_beta)

        partials['DOC', 'Cf_base'] = delta_Cf * m_fuel
        partials['DOC', 'C_time'] = R / V
        partials['DOC', 'k_acq'] = C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
        partials['DOC', 'C_eng_ref'] = k_acq * (1 + beta_base * delta_beta * SFC_tech)
        partials['DOC', 'beta_base'] = (k_acq * C_eng_ref) * (delta_beta * SFC_tech)

        partials['DOC', 'delta_Cf'] = Cf_base * m_fuel
        partials['DOC', 'delta_beta'] = (k_acq * C_eng_ref) * (beta_base * SFC_tech)

        partials['Dpm', 'm_fuel'] = partials['DOC', 'm_fuel'] / (N_pax * R)
        partials['Dpm', 'R'] = -(Cf_base * delta_Cf * m_fuel + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)) / (N_pax * R**2)
        partials['Dpm', 'V'] = partials['DOC', 'V'] / (N_pax * R)
        partials['Dpm', 'SFC_tech'] = partials['DOC', 'SFC_tech'] / (N_pax * R)
        partials['Dpm', 'Cf_base'] = partials['DOC', 'Cf_base'] / (N_pax * R)
        partials['Dpm', 'C_time'] = partials['DOC', 'C_time'] / (N_pax * R)
        partials['Dpm', 'k_acq'] = partials['DOC', 'k_acq'] / (N_pax * R)
        partials['Dpm', 'C_eng_ref'] = partials['DOC', 'C_eng_ref'] / (N_pax * R)
        partials['Dpm', 'beta_base'] = partials['DOC', 'beta_base'] / (N_pax * R)
        partials['Dpm', 'N_pax'] = -(DOC / (N_pax**2 * R))

        partials['Dpm', 'delta_Cf'] = partials['DOC', 'delta_Cf'] / (N_pax * R)
        partials['Dpm', 'delta_beta'] = partials['DOC', 'delta_beta'] / (N_pax * R)

#corresponds to uqpce main script/func
class ExampleMDA(om.Group):

    def initialize(self):
        self.options.declare('vec_size',default=1, types=int)
    
    def setup(self):
        n = self.options['vec_size']
        
        self.add_subsystem(
                            'Prop', Propulsion(vec_size=n),
                            promotes_inputs=['V', 'SFC_tech', 'delta_eta', 'delta_kv'],
                          )

        self.add_subsystem(
                            'Engine', EngineWeight(vec_size=n), 
                            promotes_inputs=['SFC_tech','delta_alpha'],
                           )

        self.add_subsystem(
                           'Aero', AeroDicipline(vec_size=n), 
                           promotes_inputs=['S', 'AR', 'V', 'delta_CD0', 'delta_ks', 'delta_e'],
                           )

        self.add_subsystem(
                           'Weight', Weights_Struct(vec_size=n),
                            promotes_inputs=['S', 'AR', 'V', 'delta_fsys','delta_kw','delta_p'],
                           )

        self.add_subsystem(
                           'Mass', TotalMassComp(vec_size=n)
                           )

        self.add_subsystem(
                            'Range', BreguetRangeComp(vec_size=n), 
                            promotes_inputs=['V']
                           )
        
        Balance = om.BalanceComp()
        Balance.add_balance(
            name='m_fuel',
            val=16000.0* np.ones(n),
            units='kg',
            lower=1000.0,
            upper=50000.0,
            lhs_name='R',
            rhs_name='R_target',
            eq_units='m',
            ref=16000.0,
            res_ref=1.0e6,
            )
        self.add_subsystem('Balance', Balance)


        self.connect('Balance.m_fuel', 'Range.m_fuel')
        self.connect('Mass.m_total', 'Range.m_total')
        self.connect('Aero.LD', 'Range.LD')
        self.connect('Prop.SFC', 'Range.SFC')
        self.connect('Range.R', 'Balance.R')
        self.connect('Balance.m_fuel', 'Mass.m_fuel')
        self.connect('Weight.m_empty', 'Mass.m_empty')
        self.connect('Mass.m_total', 'Aero.m_total')
        self.connect('Engine.m_engine', 'Weight.m_engine')
        self.connect('Mass.m_total', 'Weight.m_total')


        self.nonlinear_solver = om.NewtonSolver(solve_subsystems=True)
        self.nonlinear_solver.options['iprint'] = 2
        self.nonlinear_solver.options['maxiter'] = 500
        self.nonlinear_solver.options['atol'] = 1e-12
        self.nonlinear_solver.options['rtol'] = 1e-12

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

    script_dir = os.path.dirname(os.path.abspath(__file__))
    relative_yaml = 'input.yaml'
    relative_matrix = 'run_matrix_generated.dat'
    input_file = os.path.join(script_dir, relative_yaml)
    matrix_file  = os.path.join(script_dir, relative_matrix)

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
    
    prob.model.add_subsystem(
        'MDA', 
        ExampleMDA(vec_size=resp_cnt), 
        promotes_inputs=(['V', 'S', 'AR', 'SFC_tech',
                          'delta_eta', 'delta_kv','delta_alpha',
                          'delta_CD0','delta_ks','delta_e',
                          'delta_fsys','delta_kw','delta_p']), 
    )

    prob.model.add_subsystem(
        'CL_constraint', 
         AeroConst(vec_size=resp_cnt), 
         promotes_outputs=['CL_constraint']
    )

    prob.model.add_subsystem(
        'DOC_objective', 
        DOC(vec_size=resp_cnt), 
        promotes_inputs=(['V','SFC_tech',
                          'delta_beta','delta_Cf',]), 
        promotes_outputs=['DOC','Dpm']
    )

    prob.model.connect('MDA.Aero.CL','CL_constraint.CL')

    prob.model.connect('MDA.Balance.m_fuel','DOC_objective.m_fuel')
    prob.model.connect('MDA.Range.R','DOC_objective.R')

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
            uncert_list=['CL_constraint', 'DOC','Dpm'],
            tanh_omega=1e-3,
            sample_ref0=[0.0, 0.0, 0.0],
            sample_ref=[0.1, 5.0e4, 0.01],
        ),
        promotes_inputs=['CL_constraint', 'DOC', 'Dpm'],
        promotes_outputs=[
            'CL_constraint:resampled_responses',
            'CL_constraint:ci_lower',
            'CL_constraint:ci_upper',
            'CL_constraint:mean',

            'DOC:resampled_responses',
            'DOC:ci_lower',
            'DOC:ci_upper',
            'DOC:mean',
            'DOC:mean_plus_var',
            
            'Dpm:resampled_responses',
            'Dpm:ci_lower',
            'Dpm:ci_upper',
            'Dpm:mean',
            'Dpm:mean_plus_var'
        ]
    )


 

    """
    #---------------------------------------------------------------------------
    #                   Setting up the OpenMDAO Problem
    #---------------------------------------------------------------------------
    
    
    # Set up driver
    #prob.driver = om.pyOptSparseDriver(optimizer='SLSQP')
    #prob.driver.opt_settings['MAXIT'] = 50
    #prob.driver.opt_settings['ACC'] = 1e-8

    # Initial guesses for aircraft design variables
    

    # Add design variables and bounds
    #prob.model.add_design_var('S', lower=80.0, upper=300, ref=100.0)
    #prob.model.add_design_var('AR', lower=6.0, upper=50, ref=10.0)
    #prob.model.add_design_var('V', lower=190.0, upper=260.0, ref=230.0)
    #prob.model.add_design_var('SFC_tech', lower=-1.0, upper=1.0, ref=1.0)

    # Assign objective function and constraint in UQPCE formatting
    #obj = 'DOC:mean'
    CL_con = 'CL_constraint:ci_lower'

    #prob.model.add_objective(obj, ref=1.0e4)

    # CL_constraint = CL_target - CL
    # lower=0 means CL <= CL_target
    #prob.model.add_constraint(CL_con, equals=0)
    """
    

    prob.model.set_input_defaults('S', val=optimal['S'], units='m**2')
    prob.model.set_input_defaults('AR', val=optimal['AR'])
    prob.model.set_input_defaults('V', val=optimal['V'], units='m/s')
    prob.model.set_input_defaults('SFC_tech', val=optimal['SFC_tech'])


    prob.setup()

    initialize(prob)

    
    interface.set_vals(prob, variables, run_matrix)

    prob.run_model()

    print('Design Variable S ', prob.get_val('S'))
    print('Design Variable AR ', prob.get_val('AR'))
    print('Design Variable V ', prob.get_val('V'))
    print('Design Variable SFC_tech ', prob.get_val('SFC_tech'))

    #print(f'Constraint {CL_con}', prob.get_val(CL_con))
    #print(f'Objective {obj} is', prob.get_val(obj))

    print('Fuel mass ', prob.get_val('MDA.Balance.m_fuel'))
    print('Range ', prob.get_val('MDA.Range.R'))
    print('DOC ', prob.get_val('DOC'))
    print('Dpm ', prob.get_val('Dpm'))

    DOC_dist = prob.get_val('DOC:resampled_responses').ravel()
    DOC_ci_lower = prob.get_val('DOC:ci_lower').item()
    DOC_ci_upper = prob.get_val('DOC:ci_upper').item()
    DOC_mu = prob.get_val('DOC:mean').item()
    DOC_var_plus_mu = prob.get_val('DOC:mean_plus_var').item()
    DOC_var = DOC_var_plus_mu - DOC_mu



    dpm_dist = prob.get_val('Dpm:resampled_responses').ravel()
    Dpm_ci_lower = prob.get_val('Dpm:ci_lower').item()
    Dpm_ci_upper = prob.get_val('Dpm:ci_upper').item()
    Dpm_mu = prob.get_val('Dpm:mean').item()
    Dpm_var_plus_mu = prob.get_val('Dpm:mean_plus_var').item()
    Dpm_var = Dpm_var_plus_mu - Dpm_mu


    plt.rcParams.update({
        "text.usetex" : True,
        "font.family" : "serif"
    })

    fig, ax = plt.subplots(2)

    fig.suptitle(r"Direct Operating Cost PDFs")

    ax[0].hist(DOC_dist,bins=300,density=True)
    ax[0].axvline(DOC_ci_lower, color='red', linewidth=2,linestyle=':', label=rf"CI lower $\approx$ {DOC_ci_lower:.4f}")
    ax[0].axvline(DOC_ci_upper, color='red', linewidth=2,linestyle=':', label=rf"CI upper $\approx$ {DOC_ci_upper:.4f}")
    ax[0].set_xlabel(r"$\mathrm{DOC}$ [USD]",labelpad=15)
    ax[0].set_ylabel(r"Probability Density",labelpad=10)
    ax[0].set_title(rf"Estimated DOC Distribution: $\mu = {DOC_mu:.4f}, \ \ \sigma^2 = {DOC_var:.4e}$")
    ax[0].legend()

    ax[1].hist(dpm_dist,bins=300,density=True)
    ax[1].axvline(Dpm_ci_lower, color='red', linewidth=2, linestyle=':', label=rf"CI lower $\approx$ {Dpm_ci_lower:.4e}")
    ax[1].axvline(Dpm_ci_upper, color='red', linewidth=2,linestyle=':',label=rf"CI upper $\approx$ {Dpm_ci_upper:.4e}")
    ax[1].set_xlabel(r"$\mathrm{DOC}_{\mathrm{pkm}} \ \ [\frac{\mathrm{USD}}{\mathrm{px}\cdot\mathrm{km}}]$",labelpad=15)
    ax[1].set_ylabel(r"Probability Density",labelpad=10)
    ax[1].set_title(rf"Estimated $\mathrm{{DOC}}_{{\mathrm{{pkm}}}}$ Distribution: $\mu = {Dpm_mu:.4e}, \ \ \sigma^2 = {Dpm_var:.4e}$")
    ax[1].legend(loc="best")
    """
    ax[2].hist(m_fuel_dist,bins=300,density=True)
    ax[2].set_xlabel(r"$m_{\mathrm{fuel}}$ [kg]")
    ax[2].set_ylabel(r"Number of Responses")
    ax[2].set_title(r"Estimated $m_{\mathrm{fuel}}$ Probability Density")
    """

    fig.subplots_adjust(
    hspace=0.5,  # vertical spacing between rows
    wspace=0.3   # horizontal spacing between columns
    )

    plt.show()

    interface.analysis(prob, 'Dpm', 'input.yaml', 'run_matrix_generated.dat')
    interface.analysis(prob, 'DOC', 'input.yaml', 'run_matrix_generated.dat')

def original_main_script():
    prob = om.Problem()
    prob.model.add_subsystem('aircraft', CoupledGroup(), promotes=['*'])
    
    #fix later
    prob.model.set_input_defaults('V',units='m/s')
   
    # Optimizer
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'SLSQP'
    prob.driver.options['maxiter'] = 100
    prob.driver.options['tol'] = 1e-6
    prob.driver.options['disp'] = True

    #prob.model.set_input_defaults('aircraft.DOC.V')

    # Declare Design variables
    prob.model.add_design_var('S', lower=100.0, upper=180.0, ref=124.6)
    prob.model.add_design_var('AR', lower=7.0, upper=50.0, ref=9.45)
    prob.model.add_design_var('V', lower=200, upper=260, ref=1)
    prob.model.add_design_var('SFC_tech', lower=-1, upper=1, ref=1)

    # Declare Objective Function
    prob.model.add_objective('aircraft.DOC.DOC', ref=1.0e4)

    prob.model.add_constraint('aircraft.Balance.m_fuel', lower=1000.0, upper=50000.0, ref=16000.0)
    prob.model.add_constraint('aircraft.Aero.CL', lower=0.4, upper=0.53, ref=0.5)

    prob.setup()

    # Initial design point
    
    initialize_og(prob)

    #determining tuning parameters 

    #fig, axes = ks_kv_sweep(prob,20)

    #fig, axes = p_kv_sweep(prob,20)

    #plotting_list = eta_kv_sweep(prob,30)


    prob.run_model()

    print('\n~~~~737-800 Design~~~~\n\n')
    print('S:', prob.get_val('S'))
    print('AR:', prob.get_val('AR'))
    print('V:', prob.get_val('V'))
    print('SFC_tech:', prob.get_val('SFC_tech'))

    print('737-800 DOC estimate [$/flight]:', prob.get_val('aircraft.DOC.DOC'))

    prob.run_driver()

    #prob.check_totals(of=['aircraft.DOC.DOC'],wrt=['S', 'AR', 'SFC_tech','V'],
    #                 compact_print=True,form='central',step=1e-3)

    print('\n~~~~Optimized Design~~~~\n\n')
    print('S:', prob.get_val('S'))
    print('AR:', prob.get_val('AR'))
    print('V:', prob.get_val('V'))
    AR_temp = prob.get_val('AR')
    S_temp = prob.get_val('S')
    print('b', np.sqrt(AR_temp*S_temp))
    print('SFC_tech:', prob.get_val('SFC_tech'))

    print('\n~~~~Outputs~~~~\n\n')
    
    print('DOC [$/flight]:', prob.get_val('aircraft.DOC.DOC'))
    print('\nMASSES\n')
    print('m_total:', prob.get_val('aircraft.Mass.m_total'))
    print('m_empty:', prob.get_val('aircraft.Weight.m_empty'))
    print('m_fuel:', prob.get_val('aircraft.Balance.m_fuel'))
    print('\n~~~~\n')
    print('Range [km]:', prob.get_val('aircraft.Range.R')/1000)
    print('\n~~~~\n')
    print('Lift to Drag ratio:', prob.get_val('aircraft.Aero.LD'))
    print('Lift Coefficient:', prob.get_val('aircraft.Aero.CL'))
    print('Drag Coefficient:',prob.get_val('aircraft.Aero.CD'))
    print('\n~~~~\n')
    print('SFC:', prob.get_val('aircraft.Prop.SFC'))
    print('Reference SFC:', parameters['SFC_ref'])

def main():
    uqpce_main_script()
    #original_main_script()    
    
if __name__ == "__main__":
    main()
