import openmdao.api as om 
import numpy as np

class Weights_Struct(om.ExplicitComponent):
    """
    Evaluates the weights & structures for a coupled Breguet range with MDAO
    
    Inputs:
    Design Vars: S [m^2], AR [-], V [m/s]
    Uncertain Vars: delta_kw [kg] (wing mass), delta_fsys [-] (systems frac)
    Coupling: m_total [kg], m_engine [kg]

    Outputs:
    m_empty [kg], m_wing [kg]

    """

    def setup(self):
        self.add_input('S', val=150)
        self.add_input('AR', val=10)
        self.add_input('V', val=250)

        self.add_input('m_total')
        self.add_input('m_engine')

        #self.add_input("delta_kw")
        #self.add_input("delta_fsys")
        #self.add_input("delta_p")

        self.add_output('m_empty', val=0.0)
        self.add_output('m_wing', val=0.0)

    def initialize(self):
        self.options.declare('kw_base', default=1)
        self.options.declare('fsys_base', default=1)
        self.options.declare('p_base', default=1)
        self.options.declare('V_ref', default=250.0)
        self.options.declare('m_fuse', default=10000)

    def setup_partials(self):
        self.declare_partials('m_wing',['S','AR','V','m_total'])
        self.declare_partials('m_empty',['S','AR','V','m_total','m_engine'])

    def compute(self, inputs, outputs):
        """
        m_wing = kw_base · delta_kw · S^0.758 · AR^0.6 · m_total^0.006 · (V/V_ref)^(p_base·delta_p)

        m_empty = m_wing + m_fuse + fsys_base · delta_fsys · m_total + m_engine
        """

        kw_base = self.options['kw_base']
        fsys_base = self.options['fsys_base']
        p_base = self.options['p_base']
        V_ref = self.options['V_ref']
        m_fuse = self.options['m_fuse']

        S = inputs['S']
        AR = inputs['AR']
        V = inputs['V']
        m_total = inputs['m_total']
        m_engine = inputs['m_engine']

        delta_kw = 1.0
        delta_fsys = 1.0
        delta_p = 1.0

        m_wing = kw_base * delta_kw * (S ** 0.758) * (AR ** 0.6) * (m_total ** 0.006) * ((V/V_ref) ** (p_base * delta_p))

        outputs['m_wing'] = m_wing
        outputs['m_empty'] = m_wing + m_fuse + (fsys_base * delta_fsys * m_total) + m_engine 

    def compute_partials(self, inputs, partials):
        
        kw_base = self.options['kw_base']
        fsys_base = self.options['fsys_base']
        p_base = self.options['p_base']
        V_ref = self.options['V_ref']
        m_fuse = self.options['m_fuse']

        S = inputs['S']
        AR = inputs['AR']
        V = inputs['V']
        m_total = inputs['m_total']
        m_engine = inputs['m_engine']

        delta_kw = 1.0
        delta_fsys = 1.0
        delta_p = 1.0

        m_wing = kw_base * delta_kw * (S ** 0.758) * (AR ** 0.6) * (m_total ** 0.006) * ((V/V_ref) ** (p_base * delta_p))
        
        partials['m_wing', 'S'] = 0.758 * m_wing / S
        partials['m_wing', 'AR'] = 0.6 * m_wing / AR
        partials['m_wing', 'm_total'] = 0.006 * m_wing / m_total
        partials['m_wing', 'V'] = (p_base*delta_p) * m_wing / V

        #m_empty grads

        partials['m_empty', 'S'] = partials['m_wing', 'S']
        partials['m_empty', 'AR'] = partials['m_wing', 'AR']
        partials['m_empty', 'V'] = partials['m_wing', 'V']

        partials['m_empty', 'm_total'] = (partials['m_wing', 'm_total'] + fsys_base * delta_fsys)
        partials['m_empty', 'm_engine'] = 1.0

    def main():

        print("runs")

if __name__ == "__main__":

    prob = om.Problem()
    prob.model.add_subsystem(
        'weights',
        Weights_Struct()
    )

    prob.setup()

    prob.set_val('weights.S', 150.0)
    prob.set_val('weights.AR', 10.0)
    prob.set_val('weights.V', 250.0)

    prob.set_val('weights.m_total', 50000.0)
    prob.set_val('weights.m_engine', 4000.0)

    prob.run_model()

    print("m_wing =", prob.get_val('weights.m_wing'))
    print("m_empty =", prob.get_val('weights.m_empty'))

    #prob.check_partials(compact_print=True)