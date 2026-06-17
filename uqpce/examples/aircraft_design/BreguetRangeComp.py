import openmdao.api as om
import numpy as np

class BreguetRangeComp(om.ExplicitComponent):
    """
    Compute Breguet range from fuel mass

    Inputs:
    Design Varibale (scalar i think): V_cruise [m/s]
    Vector inputs (UQ): SFC [1/s], LD [], m_total [kg], m_fuel [kg]

    Outputs:
    Vector output: R [m]
    """

    def initialize(self):
        self.options.declare('vec_size', types=int)

    def setup(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.add_input('V', val = 230, units='m/s') #design variable

        self.add_input('SFC', val = 1.7e-4, shape=(n,), units='1/s') #vector inputs
        self.add_input('LD', val = 16, shape=(n,))
        self.add_input('m_total', val = 50000, shape=(n,), units='kg')
        self.add_input('m_fuel', val = 10000, shape=(n,), units='kg')

        self.add_output('R', val = 1e6, shape=(n,), units='m')

    def setup_partials(self):
        n= self.options['vec_size']
        indices = np.arange(n)

        self.declare_partials('R', 'V', rows= indices, cols=np.zeros(n, dtype=int))
        self.declare_partials('R', ['SFC', 'LD', 'm_total', 'm_fuel'], rows=indices, cols=indices)

    def compute (self, inputs, outputs):
        V = inputs['V']
        SFC = inputs['SFC']
        LD = inputs['LD']
        m_total = inputs['m_total']
        m_fuel = inputs['m_fuel']

        outputs['R'] = ((V / SFC) * (LD) * np.log(m_total / (m_total - m_fuel)))

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

        partials['R', 'm_total'] = ((V / SFC) * LD * (1.0 / m_total - 1.0 / (m_total - m_fuel)))

        partials['R', 'm_fuel'] = ((V / SFC) * LD * (1.0 / (m_total - m_fuel)))