import openmdao.api as om

class TotalMassComp(om.ExplicitComponent):
    """
    Component for "TotalMassComp" box containing analytical derivatives
    """
    def setup(self):
        
        #Local design variable
        self.add_input('m_empty', units='kg', desc='Empty mass')

        #Parameter
        self.add_input('m_payload', units='kg', desc='Payload mass')

        #Solver state
        self.add_input('m_fuel', units='kg', desc='Fuel mass')

        #Output
        self.add_output('m_total', units='kg', desc='Total mass')

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