import openmdao.api as om
import numpy as np
import matplotlib.pyplot as plt
#helpers
from fixed import parameters
from aero import distribute_input
#components
from aero import AeroDicipline
from BreguetRangeComp import BreguetRangeComp
from propAndCost import Propulsion
from propAndCost import EngineWeight
from propAndCost import DOC
from WeightsComp import Weights_Struct
from total_mass_comp import TotalMassComp


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



def initialize(prob):
    prob.set_val('V', parameters['V_cruise'])
    prob.set_val('S', parameters['S'])
    prob.set_val('AR', parameters['AR'])
    prob.set_val('SFC_tech', parameters['SFC_tech'])

    # Target range
    prob.set_val('aircraft.Balance.R_target', parameters['R_target'])

    # Mass parameters
    prob.set_val('aircraft.Balance.m_fuel', 9000.0)
    prob.set_val('aircraft.Weight.m_fuse', parameters['m_fuse'])
    prob.set_val('aircraft.Engine.m_eng_ref', parameters['m_eng_ref'])
    prob.set_val('aircraft.Mass.m_payload', parameters['m_payload_design'])

    # Ref/Environmental parameters
    prob.set_val('aircraft.Prop.SFC_ref', parameters['SFC_ref'])
    prob.set_val('aircraft.Prop.V_ref', parameters['V_ref'])    
    prob.set_val('aircraft.Weight.V_ref', parameters['V_ref'])
    prob.set_val('aircraft.Aero.g', 9.80665)
    prob.set_val('aircraft.Aero.rho', 0.38)
    prob.set_val('aircraft.Aero.C_D0_base', parameters['CD0_base'])
    prob.set_val('aircraft.Aero.S_0', parameters['S_naught'])
    prob.set_val('aircraft.Aero.e_base', parameters['e_oswald_base'])

    # DOC parameters
    prob.set_val('aircraft.DOC.Cf_base', parameters['Cf_base'])
    prob.set_val('aircraft.DOC.C_time', parameters['C_time'])
    prob.set_val('aircraft.DOC.k_acq', parameters['k_acq'])
    prob.set_val('aircraft.DOC.C_eng_ref', parameters['C_eng_ref'])
    prob.set_val('aircraft.DOC.N_pax', parameters['N_pax'])

    #~~~~~tuning parameters
        #fraction of total mass comprising 'systems' and stuff
    prob.set_val('aircraft.Weight.fsys_base', parameters['fsys_base'])
        #wing weight regression/fit tuning parameter
    prob.set_val('aircraft.Weight.kw_base', parameters['kw_base'])
        #off (faster) design velocity wing weight penalty exponent parameter
    prob.set_val('aircraft.Weight.p_base', parameters['p_base'])
        #tuning paramter to change effect SFC_tech has on changing SFC_ref
    prob.set_val('aircraft.Prop.eta_base', parameters['eta_base'])
        #off design veloicty penalty to increase SFC qudratically about V_ref
    prob.set_val('aircraft.Prop.kv_base', parameters['kv_base'])
        #strength of increase/decrease of amortized engine cost due to SFC_tech
    prob.set_val('aircraft.DOC.beta_base', parameters['beta_base'])
        #strength of increase/decrease of engine mass due to SFC_tech
    prob.set_val('aircraft.Engine.alpha_base', parameters['alpha_base'])
        #pretty hard to estimate this. it represents the sensitivty 
        #of the drag coefficient to changes in planform area linearized 
        #about S_ref. I have no idea what to put for this, but I chose a 
        #small value above. Note units are 1/m**2
    prob.set_val('aircraft.Aero.ks_base', parameters['ks_base'])

def main():
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

    # Declare Design variables
    prob.model.add_design_var('S', lower=100.0, upper=180.0, ref=124.6)
    prob.model.add_design_var('AR', lower=7.0, upper=50.0, ref=9.45)
    prob.model.add_design_var('V', lower=200, upper=260, ref=1)
    prob.model.add_design_var('SFC_tech', lower=-1, upper=1, ref=1.0)

    # Declare Objective Function
    prob.model.add_objective('aircraft.DOC.DOC', ref=1.0e4)

    prob.model.add_constraint('aircraft.Balance.m_fuel', lower=1000.0, upper=50000.0, ref=16000.0)
    prob.model.add_constraint('aircraft.Aero.CL', lower=0.4, upper=0.53, ref=0.5)

    prob.setup()

    # Initial design point
    
    initialize(prob)

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
    
    
if __name__ == "__main__":
    main()