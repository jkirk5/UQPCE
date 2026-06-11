import openmdao.api as om

#Import ExplicitComponents
from aero import AeroDiscipline
from WeightsComp import Weights_Struct
from propAndCost import Propulsion
from propAndCost import EngineWeight
from propAndCost import DOC
from BreguetRangeComp import BreguetRangeComp

class TotalMassComp(om.ExplicitComponent):
    """
    Component for "TotalMassComp" box containing analytical derivatives
    """
    def setup(self):
        
        #Local design variable
        self.add_input('m_empty', desc='Empty mass')

        #Parameter
        self.add_input('m_payload', desc='Payload mass')

        #Solver state
        self.add_input('m_fuel', desc='Fuel mass')

        #Output
        self.add_output('m_total', desc='Total mass')

    def setup_partials(self):
        self.declare_partials('m_total', ['m_empty', 'm_payload', 'm_fuel'])

    def compute(self, inputs, outputs):
        m_empty = inputs['m_empty']
        m_payload = inputs['m_payload']
        m_fuel = inputs['m_fuel']

        outputs['m_total'] = m_empty + m_fuel + m_payload
    
    def compute_partials(self, inputs, partials):
        partials['m_total', 'm_empty'] = 1.0
        partials['m_total', 'm_payload'] = 1.0
        partials['m_total', 'm_fuel'] = 1.0

class AeroStruct(om.Group):
    """
    Coupled solver loop with AeroComp, WeightsComp, TotalMassComp, and BreguetRangeComp
    """
    def setup(self):
        self.add_subsystem('aero', AeroDiscipline(), 
                           promotes_inputs= ['S', 'AR', 'V', 'rho', 'g', 'C_D0_base', 'ks_base', 'e_base'], 
                           promotes_outputs= [('L/D', 'LD'), 'CL'])    
    
        self.add_subsystem('mass', Weights_Struct(), 
                           promotes_inputs= ['S', 'AR', 'V', 'm_engine', 'm_total'], 
                           promotes_outputs= ['m_empty'])
        
        self.add_subsystem('total_mass', TotalMassComp(), 
                           promotes_inputs= ['m_empty', 'm_fuel', 'm_payload'], 
                           promotes_outputs= ['m_total'])
        
        self.add_subsystem('range', BreguetRangeComp(), 
                           promotes_inputs= ['LD', 'SFC', 'V', 'm_total', 'm_fuel'], 
                           promotes_outputs= [('R', 'R_comp')])
        
        #BalanceComp to determine converged value for 'm_fuel'
        bal = self.add_subsystem('range_bal', om.BalanceComp(), promotes=['*'])
        bal.add_balance(name='m_fuel', eq_units='km', lhs_name='R_comp', rhs_name='R_target')

        #Setup solvers (linear + nonlinear)
        self.nonlinear_solver = om.NewtonSolver(solve_subsystems=False)
        self.nonlinear_solver.options['iprint'] = 2
        self.nonlinear_solver.options['maxiter'] = 20
        self.linear_solver = om.DirectSolver()

#PROBLEM START
p = om.Problem()
p.model.add_subsystem('prop', Propulsion(), 
                      promotes_inputs= ['SFC_tech', ('V_cruise', 'V'), 'SFC_ref', 'eta_base', 'kv_base', 'V_ref'], 
                      promotes_outputs= ['SFC'])
        
p.model.add_subsystem('engine_weight', EngineWeight(), 
                      promotes_inputs= ['SFC_tech', 'delta_alpha', 'm_eng_ref', 'alpha_base'], 
                      promotes_outputs= ['m_engine'])

p.model.add_subsystem('aerostruct', AeroStruct(), promotes=['*'])

p.model.add_subsystem('DOC', DOC(),
                      promotes_inputs=['SFC_tech', ('V_cruise', 'V'), ('R', 'R_comp'), 'm_fuel', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base'],
                      promotes_outputs=['DOC'])

p.model.add_design_var('S', units='m**2')
p.model.add_design_var('V', units='m/s')
p.model.add_design_var('AR')
p.model.add_design_var('SFC_tech', lower=-1.0, upper=1.0)

p.model.add_constraint('CL', lower=0.0, upper=1.0) #CHANGE UPPER BOUND TO CL_MAX (STALL)

p.model.add_objective('DOC') #Units?

p.setup()

#[p.set_val() here, or fixed.py file]

""""
#Uncertain Variables
self.set_input_defaults('delta_CD0', val=1.0)
self.set_input_defaults('delta_ks', val=1.0)
self.set_input_defaults('delta_e', val=1.0)

self.set_input_defaults('delta_kw', val=1.0)
self.set_input_defaults('delta_fsys', val=1.0)
self.set_input_defaults('delta_p', val=1.0)

self.set_input_defaults('delta_eta', val=1.0)
self.set_input_defaults('delta_kv', val=1.0)
self.set_input_defaults('delta_alpha', val=1.0)

self.set_input_defaults('delta_Cf', val=1.0)
self.set_input_defaults('delta_beta', val=1.0)
"""

p.run_model()