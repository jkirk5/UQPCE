import openmdao.api as om
from aero import AeroDicipline
from BreguetRangeComp import BreguetRangeComp
from propAndCost import Propulsion
from propAndCost import EngineWeight
from propAndCost import DOC
from WeightsComp import Weights_Struct
#from mass import Residual
from total_mass import MassTotal


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
        self.add_subsystem('Mass', MassTotal())
        self.add_subsystem('Range', BreguetRangeComp(), promotes_inputs=['V'])

        Balance = om.BalanceComp()
        Balance.add_balance(
            name='m_fuel',
            val=16000.0,
            lower=1000.0,
            upper=50000.0,
            lhs_name='R',
            rhs_name='R_target',
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
        self.nonlinear_solver.options['atol'] = 1e-6
        self.nonlinear_solver.options['rtol'] = 1e-9

        self.nonlinear_solver.linesearch = om.BoundsEnforceLS()
        self.nonlinear_solver.linesearch.options['bound_enforcement'] = 'scalar'

        self.linear_solver = om.DirectSolver()

from fixed import parameters


def main():
    prob = om.Problem()
    prob.model.add_subsystem('aircraft', CoupledGroup(), promotes=['*'])

    prob.setup()

    # 737-800-ish design point
    prob.set_val('V', 235.0)        # m/s
    prob.set_val('S', 124.6)        # m^2
    prob.set_val('AR', 9.45)        # -
    prob.set_val('SFC_tech', 0.0)   # baseline

    # Target range in meters
    prob.set_val('aircraft.Balance.R_target', parameters['R_target'])

    # Fuel initial guess
    prob.set_val('aircraft.Balance.m_fuel', 9000.0)  # kg

    # Propulsion parameters
    prob.set_val('aircraft.Prop.SFC_ref', parameters['SFC_ref'])
    prob.set_val('aircraft.Prop.eta_base', parameters['eta_base'])
    prob.set_val('aircraft.Prop.kv_base', parameters['kv_base'])
    prob.set_val('aircraft.Prop.V_ref', parameters['V_ref'])

    # Engine weight parameters
    prob.set_val('aircraft.Engine.m_eng_ref', parameters['m_eng_ref'])
    prob.set_val('aircraft.Engine.alpha_base', parameters['alpha_base'])

    # Mass parameters
    prob.set_val('aircraft.Mass.m_payload', parameters['m_payload'])

    # Aero parameters
    prob.set_val('aircraft.Aero.g', 9.80665)
    prob.set_val('aircraft.Aero.rho', 0.38)  # kg/m^3, cruise altitude ballpark
    prob.set_val('aircraft.Aero.C_D0_base', parameters['CD0_base'])
    prob.set_val('aircraft.Aero.S_0', parameters['S_naught'])
    prob.set_val('aircraft.Aero.ks_base', parameters['ks_base'])
    prob.set_val('aircraft.Aero.e_base', parameters['e_oswald_base'])

    # DOC parameters
    prob.set_val('aircraft.DOC.Cf_base', parameters['Cf_base'])
    prob.set_val('aircraft.DOC.C_time', parameters['C_time'])
    prob.set_val('aircraft.DOC.k_acq', parameters['k_acq'])
    prob.set_val('aircraft.DOC.C_eng_ref', parameters['C_eng_ref'])
    prob.set_val('aircraft.DOC.beta_base', parameters['beta_base'])

    prob.run_model()

    print('Fuel mass:', prob.get_val('aircraft.Balance.m_fuel'))
    print('Range:', prob.get_val('aircraft.Range.R'))
    print('DOC:', prob.get_val('aircraft.DOC.DOC'))

    print("R after run:", prob.get_val('aircraft.Range.R'))
    print("m_fuel after run:", prob.get_val('aircraft.Balance.m_fuel'))
    print("m_total after run:", prob.get_val('aircraft.Mass.m_total'))
    print("m_empty after run:", prob.get_val('aircraft.Weight.m_empty'))
    print("LD after run:", prob.get_val('aircraft.Aero.LD'))
    print("SFC after run:", prob.get_val('aircraft.Prop.SFC'))


if __name__ == "__main__":
    main()