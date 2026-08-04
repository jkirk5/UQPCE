import openmdao.api as om
import numpy as np
from fixed import parameters

class DOC(om.ExplicitComponent):
    """
    Component for "DOCComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']

        #proposed design variables
        self.add_input('SFC_tech', units="unitless")
        self.add_input('V_cruise', units='m/s')
        
        #model variable (output from other component)
        self.add_input('R', units='m', shape=(n,))
        self.add_input('m_fuel', units='kg', shape=(n,)) 

        #uncertain parameters
        self.add_input('delta_Cf', val=np.ones(n), units="unitless", shape=(n,))
        self.add_input('delta_beta', val=np.ones(n), units="unitless", shape=(n,))

        #tuning parameters
        self.add_input('Cf_base', units='USD/kg')
        self.add_input('beta_base', units="unitless")
        
        #constant parameters
        self.add_input('C_time', val=parameters['C_time'], units='USD/s')
        self.add_input('k_acq', val=parameters['k_acq'], units="unitless")
        self.add_input('C_eng_ref', val=parameters['C_eng_ref'], units='USD')

        #outputs
        self.add_output('DOC', units='USD', shape=(n,))
       
    def setup_partials(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.declare_partials('DOC', ['V_cruise', 'SFC_tech', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base'])
        self.declare_partials('DOC', ['R', 'm_fuel', 'delta_Cf', 'delta_beta'], rows=arange, cols=arange)

    def compute(self, inputs, outputs):
 
        SFC_tech = inputs['SFC_tech']
        V_cruise = inputs['V_cruise']
        Cf_base = inputs['Cf_base']
        m_fuel = inputs['m_fuel']
        C_time = inputs['C_time']
        R = inputs['R']
        k_acq = inputs['k_acq']
        C_eng_ref = inputs['C_eng_ref']
        beta_base = inputs['beta_base']
        delta_beta = inputs['delta_beta']
        delta_Cf = inputs['delta_Cf']

        outputs['DOC'] = DOC = Cf_base * delta_Cf * m_fuel + C_time * (R/V_cruise) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
        
    def compute_partials(self, inputs, partials):
        SFC_tech = inputs['SFC_tech']
        V_cruise = inputs['V_cruise']
        Cf_base = inputs['Cf_base']
        m_fuel = inputs['m_fuel']
        C_time = inputs['C_time']
        R = inputs['R']
        k_acq = inputs['k_acq']
        C_eng_ref = inputs['C_eng_ref']
        beta_base = inputs['beta_base']
        delta_Cf = inputs['delta_Cf']
        delta_beta = inputs['delta_beta']

        # DOC = Cf_base * delta_Cf * m_fuel + C_time * (R/V) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)

        partials['DOC', 'm_fuel'] = Cf_base * delta_Cf
        partials['DOC', 'R'] = C_time / V_cruise
        partials['DOC', 'V_cruise'] = -C_time * (R / V_cruise**2)
        partials['DOC', 'SFC_tech'] = k_acq * C_eng_ref * (beta_base * delta_beta)

        partials['DOC', 'Cf_base'] = delta_Cf * m_fuel
        partials['DOC', 'C_time'] = R / V_cruise
        partials['DOC', 'k_acq'] = C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
        partials['DOC', 'C_eng_ref'] = k_acq * (1 + beta_base * delta_beta * SFC_tech)
        partials['DOC', 'beta_base'] = (k_acq * C_eng_ref) * (delta_beta * SFC_tech)

        partials['DOC', 'delta_Cf'] = Cf_base * m_fuel
        partials['DOC', 'delta_beta'] = (k_acq * C_eng_ref) * (beta_base * SFC_tech)