import openmdao.api as om 
import numpy as np
from fixed import parameters

class Weights_Struct(om.ExplicitComponent):
    """
    Evaluates the weights & structures for a coupled Breguet range with MDAO
    
    Inputs:
    Design Vars (scalar): S [m^2], AR [-], V_cruise [m/s]
    Vector coupling inputs: m_total [kg], m_engine [kg]
    Vector uncertain inputs: delta_kw, delta_fsys, delta_p
    Fixed parameters: kw_base, fsys_base, p_base, V_ref [m/s], m_fuse [kg]

    Outputs:
    Vectors: m_empty [kg], m_wing [kg]

    """
    def initialize(self):
        self.options.declare('vec_size', types=int)

    def setup(self):
        n= self.options['vec_size']

        self.add_input('S', val=parameters['S_naught'], units='m**2')
        self.add_input('AR', val=parameters['b']**2 / parameters['S_naught'])
        self.add_input('V_cruise', val=parameters['V_ref'], units='m/s')

        self.add_input('m_total', val=50000.0, shape=(n,), units='kg')
        self.add_input('m_engine', val=parameters['m_eng_ref'], shape=(n,), units='kg')

        self.add_input("delta_kw", val=1, shape=(n,)) #uncertain variables
        self.add_input("delta_fsys", val=1, shape=(n,))
        self.add_input("delta_p", val=1, shape=(n,))

        self.add_input('kw_base', val=parameters['kw_base'])
        self.add_input('fsys_base', val=parameters['fsys_base'])
        self.add_input('p_base', val=parameters['p_base'])
        self.add_input('V_ref', val=parameters['V_ref'], units='m/s')
        self.add_input('m_fuse', val=parameters['m_fuse'], units='kg')

        self.add_output('m_empty', val=0.0, shape=(n,), units= 'kg')
        self.add_output('m_wing', val=0.0, shape=(n,), units='kg')

    def setup_partials(self):
        n = self.options['vec_size']

        indices = np.arange(n)
        scalar_columns = np.zeros(n, dtype=int)

        m_wing_scalar_inputs = ['S','AR','V_cruise','kw_base','p_base','V_ref']
        m_wing_vector_inputs = ['m_total','delta_kw','delta_p']

        m_empty_scalar_inputs = ['S','AR','V_cruise','kw_base','fsys_base','p_base','V_ref','m_fuse']
        m_empty_vector_inputs = ['m_total','m_engine','delta_kw','delta_fsys','delta_p']

        self.declare_partials('m_wing',m_wing_scalar_inputs,rows=indices,cols=scalar_columns)

        self.declare_partials('m_wing',m_wing_vector_inputs,rows=indices,cols=indices)

        self.declare_partials('m_empty',m_empty_scalar_inputs,rows=indices,cols=scalar_columns)

        self.declare_partials('m_empty',m_empty_vector_inputs,rows=indices,cols=indices)

    def compute(self, inputs, outputs):
        """
        m_wing = kw_base · S^0.758 · AR^0.6 · m_total^0.006 · (V_cruise/V_ref)^p_base

        m_empty = m_wing + m_fuse + fsys_base · m_total + m_engine
        """

        S = inputs['S']
        AR = inputs['AR']
        V_cruise = inputs['V_cruise']

        m_total = inputs['m_total']
        m_engine = inputs['m_engine']

        delta_kw = inputs['delta_kw']
        delta_fsys = inputs['delta_fsys']
        delta_p = inputs['delta_p']
        
        kw_base = inputs['kw_base']
        fsys_base = inputs['fsys_base']
        p_base = inputs['p_base']
        V_ref = inputs['V_ref']
        m_fuse = inputs['m_fuse']

        m_wing = (kw_base * delta_kw * (S ** 0.758) * (AR ** 0.6) * (m_total ** 0.006) * ((V_cruise/V_ref) ** (p_base * delta_p)))

        outputs['m_wing'] = m_wing

        outputs['m_empty'] = m_wing + m_fuse + (fsys_base * m_total* delta_fsys) + m_engine 

    def compute_partials(self, inputs, partials):
        
        kw_base = inputs['kw_base']
        fsys_base = inputs['fsys_base']
        p_base = inputs['p_base']
        V_ref = inputs['V_ref']

        S = inputs['S']
        AR = inputs['AR']
        V_cruise = inputs['V_cruise']

        m_total = inputs['m_total']

        delta_kw = inputs['delta_kw']
        delta_fsys = inputs['delta_fsys']
        delta_p = inputs['delta_p']

        m_wing = (kw_base * delta_kw * (S ** 0.758) * (AR ** 0.6) * (m_total ** 0.006) * ((V_cruise/V_ref) ** (p_base * delta_p)))
        
        partials['m_wing', 'S'] = 0.758 * m_wing / S
        partials['m_wing', 'AR'] = 0.6 * m_wing / AR
        partials['m_wing', 'm_total'] = 0.006 * m_wing / m_total
        partials['m_wing', 'V_cruise'] = delta_p * p_base * m_wing / V_cruise

        partials['m_wing', 'delta_kw'] = kw_base * (S ** 0.758) * (AR ** 0.6) * (m_total ** 0.006) * ((V_cruise/V_ref) ** (p_base * delta_p))
        partials['m_wing', 'delta_p'] = m_wing * p_base * np.log(V_cruise / V_ref)
        partials['m_wing', 'kw_base'] = delta_kw * (S ** 0.758) * (AR ** 0.6) * (m_total ** 0.006) * ((V_cruise/V_ref) ** (p_base * delta_p))

        partials['m_wing', 'V_ref'] = -(p_base * delta_p) * m_wing / V_ref
        partials['m_wing', 'p_base'] = m_wing * delta_p * np.log(V_cruise/V_ref)

        #m_empty grads

        partials['m_empty', 'S'] = 0.758 * m_wing / S
        partials['m_empty', 'AR'] = 0.6 * m_wing / AR
        partials['m_empty', 'V_cruise'] = (p_base * delta_p) * m_wing / V_cruise

        partials['m_empty', 'm_total'] = 0.006 * m_wing / m_total + fsys_base * delta_fsys
        partials['m_empty', 'm_engine'] = 1.0

        partials['m_empty', 'delta_kw'] = kw_base * (S ** 0.758) * (AR ** 0.6) * (m_total ** 0.006) * ((V_cruise/V_ref) ** (p_base * delta_p))
        partials['m_empty', 'delta_fsys'] = fsys_base * m_total
        partials['m_empty', 'delta_p'] = m_wing * p_base * np.log(V_cruise/V_ref)

        partials['m_empty', 'kw_base'] = delta_kw * (S ** 0.758) * (AR ** 0.6) * (m_total ** 0.006) * ((V_cruise/V_ref) ** (p_base * delta_p))
        partials['m_empty', 'fsys_base'] = m_total * delta_fsys

        partials['m_empty', 'p_base'] = m_wing * delta_p * np.log(V_cruise/V_ref)
        partials['m_empty', 'V_ref'] = -(p_base * delta_p) * m_wing / V_ref

        partials['m_empty', 'm_fuse'] = 1.0