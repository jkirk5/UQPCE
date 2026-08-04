import openmdao.api as om
import numpy as np
from fixed import parameters

class PropulsionComp(om.ExplicitComponent):
    """
    Component for "PropulsionComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']

        #Parameters
        
        #proposed design variables
        self.add_input('SFC_tech', units="unitless")
        self.add_input('V_cruise', units='m/s')

        #model variable (output from other component)

        #uncertain parameters
        self.add_input('delta_eta', val=np.ones(n), units="unitless", shape=(n,))
        self.add_input('delta_kv', val=np.ones(n), units="unitless", shape=(n,))
        
        #tuning parameters
        self.add_input('eta_base', units="unitless")
        self.add_input('kv_base', units="unitless")

        #constant parameters
        self.add_input('SFC_ref', val=parameters['SFC_ref'], units='1/s')
        self.add_input('V_ref', val=parameters['V_ref'], units="m/s")

        #outputs
        self.add_output('SFC', units="1/s", shape=(n,))

    def setup_partials(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.declare_partials('SFC', ['SFC_tech', 'V_cruise', 'SFC_ref', 'eta_base', 'kv_base', 'V_ref'])
        self.declare_partials('SFC', ['delta_eta', 'delta_kv'], rows=arange, cols=arange)

    def compute(self, inputs, outputs):
        """
        SFC = SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (1 + kv_base * delta_kv * (V/V_ref - 1)^2)
        """
        SFC_ref = inputs['SFC_ref']
        eta_base = inputs['eta_base']
        kv_base = inputs['kv_base']
        V_ref = inputs['V_ref']
        SFC_tech = inputs['SFC_tech']
        V_cruise = inputs['V_cruise']
        delta_eta = inputs['delta_eta']
        delta_kv = inputs['delta_kv']
        
        outputs['SFC'] = SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)**2)
    
    def compute_partials(self, inputs, partials):
        SFC_ref = inputs['SFC_ref']
        eta_base = inputs['eta_base']
        kv_base = inputs['kv_base']
        V_ref = inputs['V_ref']
        SFC_tech = inputs['SFC_tech']
        V_cruise = inputs['V_cruise']
        delta_eta = inputs['delta_eta']
        delta_kv = inputs['delta_kv']
        
        partials['SFC', 'SFC_tech'] = SFC_ref * (-eta_base * delta_eta) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)**2)
        partials['SFC', 'V_cruise'] = (2 / V_ref) * (SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (kv_base * delta_kv * (V_cruise/V_ref - 1)))
        
        partials['SFC', 'SFC_ref'] = (1 - eta_base * delta_eta * SFC_tech) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)**2)
        partials['SFC', 'eta_base'] = SFC_ref * (-delta_eta * SFC_tech) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)**2)
        partials['SFC', 'kv_base'] = SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (delta_kv * (V_cruise/V_ref - 1)**2)
        partials['SFC', 'V_ref'] = (-2 * V_cruise / V_ref**2) * (SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (kv_base * delta_kv * (V_cruise/V_ref - 1)))

        partials['SFC', 'delta_eta'] = SFC_ref * (-eta_base * SFC_tech) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)**2)
        partials['SFC', 'delta_kv'] = SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (kv_base * (V_cruise/V_ref - 1)**2)