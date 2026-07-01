import openmdao.api as om
import numpy as np
#hi
class TotalMassComp(om.ExplicitComponent):
    """
    Component for "TotalMassComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', types=int)
    
    def setup(self):
        n = self.options['vec_size']

        #Local design variable
        self.add_input('m_empty', units='kg', desc='Empty mass', shape=(n,))

        #Parameter
        self.add_input('m_payload', units='kg', desc='Payload mass')

        #Solver state
        self.add_input('m_fuel', units='kg', desc='Fuel mass', shape=(n,))

        #Output
        self.add_output('m_total', units='kg', desc='Total mass', shape=(n,))

    def setup_partials(self):
        n = self.options['vec_size']
        arange = np.arange(n)
        
        self.declare_partials('m_total', ['m_empty', 'm_payload'])
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