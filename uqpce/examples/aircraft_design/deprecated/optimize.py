import openmdao.api as om
from disciplines.objective import *
from disciplines.BreguetRange import *
from disciplines.aero import *
from disciplines.total_mass_comp import *
from disciplines.propulsion import *
from disciplines.weight import *
from disciplines.doc import DOC
from disciplines.dpm import Dpm
from fixed import parameters
from helpers import *

from uqpce.mdao.uqpcegroup import UQPCEGroup
from uqpce.mdao import interface
import os
class CoupledGroup(om.Group):

    def setup(self):
        # 737-800-ish baseline
        self.set_input_defaults('S', val=124.6)       # m^2
        self.set_input_defaults('AR', val=9.45)       # -
        self.set_input_defaults('V', val=235.0)       # m/s
        self.set_input_defaults('SFC_tech', val=0.0)  # baseline technology

        self.add_subsystem('Prop', PropulsionComp(vec_size=1), promotes_inputs=['V', 'SFC_tech'])

        self.add_subsystem('Engine', EngineWeightComp(vec_size=1), promotes_inputs=['SFC_tech'])
        
        #^^add at problem level

        self.add_subsystem('Aero', AeroComp(vec_size=1), promotes_inputs=['S', 'AR', 'V'])
        
        self.add_subsystem('Weight', WeightsComp(vec_size=1), promotes_inputs=['S', 'AR', 'V'])
        
        self.add_subsystem('Mass', TotalMassComp(vec_size=1))
        
        self.add_subsystem('Range', BreguetRangeComp(vec_size=1), promotes_inputs=['V'])

        

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
                           promotes_outputs=['m_fuel'])

        
        self.add_subsystem('DOC', DOC(vec_size=1), promotes_inputs=['V', 'SFC_tech'])
        self.add_subsystem('Dpm', Dpm(vec_size=1))

        self.connect('m_fuel', 'Range.m_fuel')
        self.connect('Mass.m_total', 'Range.m_total')
        self.connect('Aero.LD', 'Range.LD')
        self.connect('Prop.SFC', 'Range.SFC')
        self.connect('Range.R', 'Balance.R')
        self.connect('m_fuel', 'Mass.m_fuel')
        self.connect('Weight.m_empty', 'Mass.m_empty')
        self.connect('Mass.m_total', 'Aero.m_total')
        self.connect('Engine.m_engine', 'Weight.m_engine')
        self.connect('Mass.m_total', 'Weight.m_total')
        self.connect('Range.R', 'DOC.R')
        self.connect('m_fuel', 'DOC.m_fuel')
        self.connect('Range.R', 'Dpm.R')
        self.connect('DOC.DOC', 'Dpm.DOC')

        self.nonlinear_solver = om.NewtonSolver(solve_subsystems=True)
        self.nonlinear_solver.options['iprint'] = 2
        self.nonlinear_solver.options['maxiter'] = 500
        self.nonlinear_solver.options['atol'] = 1e-12
        self.nonlinear_solver.options['rtol'] = 1e-12

        self.nonlinear_solver.linesearch = om.BoundsEnforceLS()
        self.nonlinear_solver.linesearch.options['bound_enforcement'] = 'scalar'

        self.linear_solver = om.DirectSolver()

def original_main_script():

    prob = om.Problem()
    prob.model.add_subsystem('aircraft', CoupledGroup(), promotes=['*'])
    
    #fix later
    prob.model.set_input_defaults('V',units='m/s')
   
    # Optimizer
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'SLSQP'
    prob.driver.options['maxiter'] = 100
    prob.driver.options['tol'] = 1e-12
    prob.driver.options['disp'] = True

    #prob.model.set_input_defaults('aircraft.DOC.V')

    # Declare Design variables
    prob.model.add_design_var('S', lower=100.0, upper=180.0, ref=124.6)
    prob.model.add_design_var('AR', lower=7.0, upper=50.0, ref=9.45)
    prob.model.add_design_var('V', lower=200, upper=260, ref=1)
    prob.model.add_design_var('SFC_tech', lower=-1, upper=1, ref=1)

    # Declare Objective Function
    #prob.model.add_objective('aircraft.DOC.DOC', ref=1.0e4)
    prob.model.add_objective('aircraft.Dpm.Dpm', ref=1.0e-2)


    prob.model.add_constraint('aircraft.Balance.m_fuel', lower=1000.0, upper=50000.0, ref=16000.0)
    prob.model.add_constraint('aircraft.Aero.CL', upper = 0.53, ref=0.1)
    #prob.model.add_constraint('aircraft.Aero.WL', equals=parameters['wing_load'],ref=1000)

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

    #prob.run_driver()

    #prob.check_totals(of=['aircraft.DOC.DOC'],wrt=['S', 'AR', 'SFC_tech','V'],
                    # compact_print=True, method='fd')

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
    print('Dpm [$/flight/px*km]:', prob.get_val('aircraft.Dpm.Dpm'))
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
    original_main_script()

if __name__ == "__main__":
    main()