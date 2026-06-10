import openmdao.api as om
import numpy as np

class BreguetRangeComp(om.ExplicitComponent):
    """
    Compute Breguet range from fuel mass

    Inputs:
    Design Vars: V [m/s]
    Uncertain Vars: delta_kw [kg] (wing mass), delta_fsys [-] (systems frac)
    Coupling: m_total [kg], L/D [-], SFC [kg/Ns]

    Outputs:
    R [m]

    """

    def setup(self):
        self.add_input('V', val = 250)
        self.add_input('SFC', val = 1.5e-5)
        self.add_input('LD', val = 15)
        self.add_input('m_total', val = 50000)
        self.add_input('m_fuel', val = 50000)

        self.add_output('R', val = 1e6)

    def setup_partials(self):
        self.declare_partials('R', ['V', 'SFC', 'LD', 'm_total', 'm_fuel'])

    def compute (self, inputs, outputs):
        V = inputs['V']
        SFC = inputs['SFC']
        LD = inputs['LD']
        m_total = inputs['m_total']
        m_fuel = inputs['m_fuel']

        outputs['R'] = (V / SFC) * (LD) * np.log(m_total / (m_total - m_fuel))

    def compute_partials(self, inputs, partials): 
        V = inputs['V']
        SFC = inputs['SFC']
        LD = inputs['LD']
        m_total = inputs['m_total']
        m_fuel = inputs['m_fuel']

        thelog = np.log(m_total / (m_total - m_fuel))

        # R = (V/SFC)*LD*ln(m_total/(m_total - m_fuel))

        partials['R', 'V'] = (1.0 / SFC) * LD * thelog

        partials['R', 'SFC'] = -(V / SFC**2) * LD * thelog

        partials['R', 'LD'] = (V / SFC) * thelog

        #ln(m_total/(m_total-m_fuel))

        partials['R', 'm_total'] = (
            (V / SFC)
            * LD
            * (1.0 / m_total - 1.0 / (m_total - m_fuel))
        )

        # d/dm_fuel ln(m_total/(m_total-m_fuel))
        # = 1/(m_total-m_fuel)
        partials['R', 'm_fuel'] = (
            (V / SFC)
            * LD
            * (1.0 / (m_total - m_fuel))
        )