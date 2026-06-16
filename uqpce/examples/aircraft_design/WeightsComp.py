import openmdao.api as om 
import numpy as np

class Weights_Struct(om.ExplicitComponent):
    """
    Evaluates the weights & structures for a coupled Breguet range with MDAO
    
    Inputs:
    Design Vars: S [m^2], AR [-], V [m/s]
    Coupling: m_total [kg], m_engine [kg]
    Parameters: kw_base, fsys_base, p_base, V_ref [m/s], m_fuse [kg]

    Outputs:
    m_empty [kg], m_wing [kg]

    """

    def setup(self):
        self.add_input('S', val=150, units='m**2')
        self.add_input('AR', val=10)
        self.add_input('V', val=250, units='m/s')

        self.add_input('m_total', val=50000, units='kg')
        self.add_input('m_engine', val=4000, units='kg')

        #self.add_input("delta_kw")
        #self.add_input("delta_fsys")
        #self.add_input("delta_p")

        self.add_input('kw_base', val=1)
        self.add_input('fsys_base', val=0.15)
        self.add_input('p_base', val=1)
        self.add_input('V_ref', val=250.0, units='m/s')
        self.add_input('m_fuse', val=10000, units='kg')

        self.add_output('m_empty', val=0.0, units= 'kg')
        self.add_output('m_wing', val=0.0, units='kg')

    def setup_partials(self):
        inputs = ['S', 'AR', 'V', 'm_total', 'm_engine', 'kw_base', 'fsys_base', 'p_base', 'V_ref', 'm_fuse']

        self.declare_partials('m_wing', inputs)
        self.declare_partials('m_empty',inputs)

    def compute(self, inputs, outputs):
        """
        m_wing = kw_base · S^0.758 · AR^0.6 · m_total^0.006 · (V/V_ref)^p_base

        m_empty = m_wing + m_fuse + fsys_base · m_total + m_engine
        """

        S = inputs['S']
        AR = inputs['AR']
        V = inputs['V']
        m_total = inputs['m_total']
        m_engine = inputs['m_engine']

        #delta_kw = 1.0
        #delta_fsys = 1.0
        #delta_p = 1.0

        kw_base = inputs['kw_base']
        fsys_base = inputs['fsys_base']
        p_base = inputs['p_base']
        V_ref = inputs['V_ref']
        m_fuse = inputs['m_fuse']

        m_wing = (kw_base * (S ** 0.758) * (AR ** 0.6) * (m_total ** 0.006) * ((V/V_ref) ** (p_base)))

        outputs['m_wing'] = m_wing

        outputs['m_empty'] = m_wing + m_fuse + (fsys_base * m_total) + m_engine 

    def compute_partials(self, inputs, partials):
        
        kw_base = inputs['kw_base']
        fsys_base = inputs['fsys_base']
        p_base = inputs['p_base']
        V_ref = inputs['V_ref']

        S = inputs['S']
        AR = inputs['AR']
        V = inputs['V']
        m_total = inputs['m_total']

        #delta_kw = 1.0
        #delta_fsys = 1.0
        #delta_p = 1.0

        m_wing = (kw_base * (S ** 0.758) * (AR ** 0.6) * (m_total ** 0.006) * ((V/V_ref) ** (p_base)))
        
        partials['m_wing', 'S'] = 0.758 * m_wing / S
        partials['m_wing', 'AR'] = 0.6 * m_wing / AR
        partials['m_wing', 'm_total'] = 0.006 * m_wing / m_total
        partials['m_wing', 'V'] = p_base * m_wing / V

        partials['m_wing', 'm_engine'] = 0.0
        partials['m_wing', 'fsys_base'] = 0.0
        partials['m_wing', 'm_fuse'] = 0.0

        partials['m_wing', 'kw_base'] = m_wing / kw_base

        partials['m_wing', 'V_ref'] = -p_base * m_wing / V_ref
        partials['m_wing', 'p_base'] = m_wing * np.log(V/V_ref)

        #m_empty grads

        partials['m_empty', 'S'] = partials['m_wing', 'S']
        partials['m_empty', 'AR'] = partials['m_wing', 'AR']
        partials['m_empty', 'V'] = partials['m_wing', 'V']

        partials['m_empty', 'm_total'] = (partials['m_wing', 'm_total'] + fsys_base)
        partials['m_empty', 'm_engine'] = 1.0

        partials['m_empty', 'kw_base'] = partials['m_wing', 'kw_base']
        partials['m_empty', 'fsys_base'] = m_total

        partials['m_empty', 'p_base'] = partials['m_wing', 'p_base']
        partials['m_empty', 'V_ref'] = partials['m_wing', 'V_ref']

        partials['m_empty', 'm_fuse'] = 1.0