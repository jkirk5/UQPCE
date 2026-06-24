import openmdao.api as om
import numpy as np

class Propulsion(om.ExplicitComponent):
    """
    Component for "PropulsionComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', types=int)

    def setup(self):
        n = self.options['vec_size']

        #Parameters
        self.add_input('SFC_ref', units='1/s', desc="Reference SFC technology factor")
        self.add_input('eta_base')
        self.add_input('kv_base')
        self.add_input('V_ref', units="m/s", desc="Reference flight speed")

        #Global design variables
        self.add_input('SFC_tech', val=0., desc="SFC technology factor")
        self.add_input('V_cruise', desc="Cruise speed")

        #Uncertainties
        self.add_input('delta_eta', val=1.0, shape=(n,))
        self.add_input('delta_kv', val=1.0, shape=(n,))

        #Output
        self.add_output('SFC', units="1/s", desc="Specific fuel consumption", shape=(n,))

    def setup_partials(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.declare_partials('SFC', ['SFC_tech', 'V_cruise', 'SFC_ref', 'eta_base', 'kv_base', 'V_ref'])
        self.declare_partials('SFC', ['delta_eta', 'delta_kv'], rows=arange, cols=arange)

    def compute(self, inputs, outputs):
        """
        SFC = SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)^2)
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

class EngineWeight(om.ExplicitComponent):
    """
    Component for "EngineWeightComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', types=int)

    def setup(self):
        n = self.options['vec_size']

        #Parameters
        self.add_input('m_eng_ref', units='kg')
        self.add_input('alpha_base')

        #Global design variables
        self.add_input('SFC_tech', val=0., desc='SFC technology factor')
    
        #Uncertainties
        self.add_input('delta_alpha', val=1.0, size=(n,))

        #Output
        self.add_output('m_engine', units='kg', desc='Engine mass', size=(n,))

    def setup_partials(self):
        n = self.options['vec_size']
        arange = np.arange(n)
        
        self.declare_partials('m_engine', ['SFC_tech', 'm_eng_ref', 'alpha_base'])
        
        self.declare_partials('m_engine', ['delta_alpha'], rows=arange, cols=arange)

    def compute(self, inputs, outputs):
        """
        m_engine = m_eng_ref * (1 + alpha_base * delta_alpha * SFC_tech)
        """
        SFC_tech = inputs['SFC_tech']
        m_eng_ref = inputs['m_eng_ref']
        alpha_base = inputs['alpha_base']
        delta_alpha = inputs['delta_alpha']
        
        outputs['m_engine'] = m_eng_ref * (1 + alpha_base * delta_alpha * SFC_tech)
    
    def compute_partials(self, inputs, partials):
        m_eng_ref = inputs['m_eng_ref']
        alpha_base = inputs['alpha_base']
        SFC_tech = inputs['SFC_tech']
        delta_alpha = inputs['delta_alpha']
        
        partials['m_engine', 'SFC_tech'] = m_eng_ref * (alpha_base * delta_alpha)

        partials['m_engine', 'm_eng_ref'] = (1 + alpha_base * delta_alpha * SFC_tech)
        partials['m_engine', 'alpha_base'] = m_eng_ref * (delta_alpha * SFC_tech)

        partials['m_engine', 'delta_alpha'] = m_eng_ref * (alpha_base * SFC_tech)

class DOC(om.ExplicitComponent):
    """
    Component for "DOCComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', types=int)

    def setup(self):
        n = self.options['vec_size']

        #Parameters
        self.add_input('Cf_base', units='USD/kg')
        self.add_input('C_time', units='USD/s')
        self.add_input('k_acq')
        self.add_input('C_eng_ref', units='USD')
        self.add_input('beta_base')

        self.add_input('N_pax', desc="Number of passengers")

        #Global design variables
        self.add_input('SFC_tech', val=0., desc='SFC technology factor')
        self.add_input('V_cruise', units='m/s', desc='Cruise speed')

        #Local design variable
        self.add_input('R', units='m', desc='Breguet range')
        
        #Solver state
        self.add_input('m_fuel', units='kg', desc='Fuel mass') 

        #Uncertainties
        self.add_input('delta_Cf', val=1.0, shape=(n,))
        self.add_input('delta_beta', val=1.0, shape=(n,))

        #Output
        self.add_output('DOC', units='USD', desc="Direct operating cost", size=(n,))

        self.add_output('Dpm', desc="DOC/pax*km", size=(n,))

    def setup_partials(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.declare_partials('DOC', ['m_fuel', 'R', 'V_cruise', 'SFC_tech', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base'])
        self.declare_partials('DOC', ['delta_Cf', 'delta_beta'], rows=arange, cols=arange)

        self.declare_partials('Dpm', ['m_fuel', 'R', 'V_cruise', 'SFC_tech', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base', 'N_pax', 'R'])
        self.declare_partials('DOC', ['delta_Cf', 'delta_beta'], rows=arange, cols=arange)

    def compute(self, inputs, outputs):
        """
        DOC = Cf_base * delta_Cf * m_fuel + C_time * (R / V_cruise) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
        """

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

        N_pax = inputs['N_pax']

        outputs['DOC'] = DOC = Cf_base * delta_Cf * m_fuel + C_time * (R/V_cruise) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)

        outputs['Dpm'] = DOC / (N_pax * R)
    
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

        N_pax = inputs['N_pax']

        DOC = Cf_base * delta_Cf * m_fuel + C_time * (R/V_cruise) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)

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

        partials['Dpm', 'm_fuel'] = partials['DOC', 'm_fuel'] / (N_pax * R)
        partials['Dpm', 'R'] = -(Cf_base * delta_Cf * m_fuel + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)) / (N_pax * R**2)
        partials['Dpm', 'V_cruise'] = partials['DOC', 'V_cruise'] / (N_pax * R)
        partials['Dpm', 'SFC_tech'] = partials['DOC', 'SFC_tech'] / (N_pax * R)
        partials['Dpm', 'Cf_base'] = partials['DOC', 'Cf_base'] / (N_pax * R)
        partials['Dpm', 'C_time'] = partials['DOC', 'C_time'] / (N_pax * R)
        partials['Dpm', 'k_acq'] = partials['DOC', 'k_acq'] / (N_pax * R)
        partials['Dpm', 'C_eng_ref'] = partials['DOC', 'C_eng_ref'] / (N_pax * R)
        partials['Dpm', 'beta_base'] = partials['DOC', 'beta_base'] / (N_pax * R)
        partials['Dpm', 'N_pax'] = -(DOC / (N_pax**2 * R))

        partials['Dpm', 'delta_Cf'] = partials['DOC', 'delta_Cf'] / (N_pax * R)
        partials['Dpm', 'delta_beta'] = partials['DOC', 'delta_beta'] / (N_pax * R)