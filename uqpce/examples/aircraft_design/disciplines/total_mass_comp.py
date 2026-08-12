import openmdao.api as om
import numpy as np
from fixed import parameters

class TotalMassComp(om.ExplicitComponent):
    """
    Component for "TotalMassComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)
    
    def setup(self):
        n = self.options['vec_size']

        #proposed design variables
        #n/a

        #model variable (output from other component)
        self.add_input('m_empty', units='kg', shape=(n,))
        self.add_input('m_fuel', units='kg', shape=(n,))

        #uncertain parameters
        #n/a

        #tuning parameters
        #n/a

        #constant parameters
        self.add_input('m_payload', val=parameters['m_payload_design'], units='kg')

        #outputs
        self.add_output('m_total', units='kg', shape=(n,))

    def setup_partials(self):
        n = self.options['vec_size']
        arange = np.arange(n)
        
        self.declare_partials('m_total', ['m_payload'])
        self.declare_partials('m_total', ['m_empty', 'm_fuel'], rows=arange, cols=arange)

    def compute(self, inputs, outputs):
        m_empty = inputs['m_empty']
        m_payload = inputs['m_payload']
        m_fuel = inputs['m_fuel']

        outputs['m_total'] = m_empty + m_fuel + m_payload
    
    def compute_partials(self, inputs, partials):
        partials['m_total', 'm_empty'] = 1.0
        partials['m_total', 'm_payload'] = 1.0
        partials['m_total', 'm_fuel'] = 1.0