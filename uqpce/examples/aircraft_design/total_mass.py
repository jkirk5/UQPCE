import openmdao.api as om
from fixed import parameters

class MassTotal(om.ExplicitComponent):

    def setup(self):
        self.add_input('m_empty', val=10000)
        self.add_input('m_fuel', val=10000)
        #fixed later  
        self.add_input('m_payload', val=10000)
        self.add_output('m_total', val=100000)

    def setup_partials(self):
        self.declare_partials('m_total','m_empty',method='exact')
        self.declare_partials('m_total','m_fuel',method='exact')

    def compute(self,inputs,outputs):
        m_empty = inputs['m_empty']
        m_fuel = inputs['m_fuel']
        m_payload = inputs['m_payload']
        outputs['m_total'] = m_empty + m_fuel + m_payload 

    def compute_partials(self, inputs, partials):
        partials['m_total','m_empty'] = 1.0
        partials['m_total','m_fuel'] = 1.0
        
        

    
    
