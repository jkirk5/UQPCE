import openmdao.api as om
import numpy as np
from fixed import parameters

class BreguetRangeComp(om.ExplicitComponent):
    """
    Component for "BreguetRangeComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']
       
        self.add_input('V_cruise', units='m/s') #design variable

        self.add_input('SFC',units='1/s',
                       shape=(n,)) #vector inputs
        self.add_input('LD',units="unitless",
                        shape=(n,))
        self.add_input('m_total', units='kg',
                       shape=(n,))
        self.add_input('m_fuel', units='kg', 
                       shape=(n,))

        self.add_output('R', units='m',
                        shape=(n,))

    def setup_partials(self):
        n= self.options['vec_size']
        indices = np.arange(n)

        self.declare_partials('R', ['V_cruise'], rows= indices, cols=np.zeros(n, dtype=int))
        self.declare_partials('R', ['SFC', 'LD', 'm_total', 'm_fuel'], rows=indices, cols=indices)

    def compute (self, inputs, outputs):
        V = inputs['V_cruise']
        SFC = inputs['SFC']
        LD = inputs['LD']
        m_total = inputs['m_total']
        m_fuel = inputs['m_fuel']

        outputs['R'] = ((V / SFC) * (LD) * np.log(m_total / (m_total - m_fuel)))

    def compute_partials(self, inputs, partials): 
        V = inputs['V_cruise']
        SFC = inputs['SFC']
        LD = inputs['LD']
        m_total = inputs['m_total']
        m_fuel = inputs['m_fuel']

        thelog = np.log(m_total / (m_total - m_fuel))

        # R = (V/SFC)*LD*ln(m_total/(m_total - m_fuel))

        partials['R', 'V_cruise'] = (1.0 / SFC) * LD * thelog

        partials['R', 'SFC'] = -(V / SFC**2) * LD * thelog

        partials['R', 'LD'] = (V / SFC) * thelog

        #ln(m_total/(m_total-m_fuel))

        partials['R', 'm_total'] = ((V / SFC) * LD * (1.0 / m_total - 1.0 / (m_total - m_fuel)))

        partials['R', 'm_fuel'] = ((V / SFC) * LD * (1.0 / (m_total - m_fuel)))