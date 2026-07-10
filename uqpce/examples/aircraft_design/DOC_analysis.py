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

# DOEDriver
prob.driver = om.DOEDriver(om.UniformGenerator(num_samples=100))
prob.driver.add_recorder(om.SqliteRecorder("doe_driver.sql"))

# Declare Design Variables (that you want to investigate in DOE)
# prob.model.add_design_var('S', lower=100.0, upper=180.0, ref=124.6, units='m**2')
# prob.model.add_design_var('AR', lower=7.0, upper=50.0, ref=9.45)
# prob.model.add_design_var('V_cruise', lower=200, upper=260, ref=1, units='m/s')
# prob.model.add_design_var('SFC_tech', lower=-1, upper=1, ref=1)
# prob.model.add_design_var('Cf_base', lower=0, upper=2, units='USD/kg')
prob.model.add_design_var('beta_base', lower=0, upper=1)

# Declare Objective and Constraint Functions
prob.model.add_objective('Dpm', ref=1.0e-1)
prob.model.add_constraint('CL', lower=0.4, upper=0.53, ref=0.5)

prob.setup()

# Initial design points
initialize_og(prob)

prob.run_driver()

# Get results
cr = om.CaseReader(prob.get_outputs_dir() / "doe_driver.sql");
cases = cr.list_cases('driver', out_stream=None)

S_array = []
AR_array = []
V_cruise_array = []
SFC_tech_array = []
Dpm_array = []
Cf_base_array = []
beta_base_array = []
for case in cases:
    outputs = cr.get_case(case).outputs;
    # S_array.append(outputs['S'])
    # AR_array.append(outputs['AR'])
    # V_cruise_array.append(outputs['V_cruise'])
    # SFC_tech_array.append(outputs['SFC_tech'])
    # Cf_base_array.append(outputs['Cf_base'])
    beta_base_array.append(outputs['beta_base'])
    Dpm_array.append(outputs['Dpm'])

plt.plot(beta_base_array, Dpm_array, 'o')
plt.show()