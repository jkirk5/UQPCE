import openmdao.api as om

class Propulsion(om.ExplicitComponent):
    """
    Component for "PropulsionComp" box containing analytical derivatives
    """
    def setup(self):
        
        #Parameters
        self.add_input('SFC_ref', desc="Reference SFC technology factor")
        self.add_input('eta_base')
        self.add_input('kv_base')
        self.add_input('V_ref', units="m/s", desc="Reference flight speed") #reference cruise speed?

        #Global design variables
        self.add_input('SFC_tech', val=0., desc="SFC technology factor")
        self.add_input('V_cruise', units="m/s", desc="Cruise speed")

        #Uncertainties
        self.add_input('delta_eta', val=1.0)
        self.add_input('delta_kv', val=1.0)

        #Output
        self.add_output('SFC', units="mg/(N*s)", desc="Specific fuel consumption")

    def setup_partials(self):
        self.declare_partials('SFC', ['SFC_tech', 'V_cruise', 'SFC_ref', 'eta_base', 'kv_base', 'V_ref'])

    def compute(self, inputs, outputs):
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

class EngineWeight(om.ExplicitComponent):
    """
    Component for "EngineWeightComp" box containing analytical derivatives
    """
    def setup(self):
        
        #Parameters
        self.add_input('m_eng_ref')
        self.add_input('alpha_base')

        #Global design variables
        self.add_input('SFC_tech', val=0., desc="SFC technology factor")
    
        #Uncertainties
        self.add_input('delta_alpha', val=1.0)

        #Output
        self.add_output('m_engine', units="kg", desc="Engine mass")

    def setup_partials(self):
        self.declare_partials('m_engine', ['SFC_tech', 'm_eng_ref', 'alpha_base'])

    def compute(self, inputs, outputs):
        SFC_tech = inputs['SFC_tech']
        m_eng_ref = inputs['m_eng_ref']
        alpha_base = inputs['alpha_base']
        delta_alpha = inputs['delta_alpha']
        
        outputs['m_engine'] = m_eng_ref * (1 + alpha_base * delta_alpha * SFC_tech)
    
    def compute_partials(self, inputs, partials):
        m_eng_ref = inputs['m_eng_ref']
        alpha_base = inputs['alpha_base']
        delta_alpha = inputs['delta_alpha']
        SFC_tech = inputs['SFC_tech']        
        
        partials['m_engine', 'SFC_tech'] = m_eng_ref * (alpha_base * delta_alpha)

        partials['m_engine', 'm_eng_ref'] = (1 + alpha_base * delta_alpha * SFC_tech)
        partials['m_engine', 'alpha_base'] = m_eng_ref * (delta_alpha * SFC_tech)

class DOC(om.ExplicitComponent):
    """
    Component for "DOCComp" box containing analytical derivatives
    """
    def setup(self):
        
        #Parameters
        self.add_input('Cf_base')
        self.add_input('C_time')
        self.add_input('k_acq')
        self.add_input('C_eng_ref')
        self.add_input('beta_base')

        #Global design variables
        self.add_input('SFC_tech', val=0., desc="SFC technology factor")
        self.add_input('V_cruise', units="m/s", desc="Cruise speed")

        #Local design variable
        self.add_input('R', units="km", desc="Breguet range")
        
        #Solver state
        self.add_input('m_fuel', units="kg", desc="Fuel mass") 

        #Uncertainties
        self.add_input('delta_Cf', val=1.0)
        self.add_input('delta_beta', val=1.0)

        #Output
        self.add_output('DOC', desc="Direct operating cost")

    def setup_partials(self):
        self.declare_partials('DOC', ['m_fuel', 'R', 'V_cruise', 'SFC_tech', 'Cf_base', 'C_time', 'k_acq', 'C_eng_ref', 'beta_base'])

    def compute(self, inputs, outputs):
        SFC_tech = inputs['SFC_tech']
        V_cruise = inputs['V_cruise']
        Cf_base = inputs['Cf_base']
        delta_Cf = inputs['delta_Cf']
        m_fuel = inputs['m_fuel']
        C_time = inputs['C_time']
        R = inputs['R']
        k_acq = inputs['k_acq']
        C_eng_ref = inputs['C_eng_ref']
        beta_base = inputs['beta_base']
        delta_beta = inputs['delta_beta']

        outputs['DOC'] = Cf_base * delta_Cf * m_fuel + C_time * (R/V_cruise) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
    
    def compute_partials(self, inputs, partials):
        V_cruise = inputs['V_cruise']
        Cf_base = inputs['Cf_base']
        delta_Cf = inputs['delta_Cf']
        C_time = inputs['C_time']
        R = inputs['R']
        k_acq = inputs['k_acq']
        C_eng_ref = inputs['C_eng_ref']
        beta_base = inputs['beta_base']
        delta_beta = inputs['delta_beta']
        m_fuel = inputs['m_fuel']
        SFC_tech = inputs['SFC_tech']
        
        partials['DOC', 'm_fuel'] = Cf_base * delta_Cf
        partials['DOC', 'R'] = C_time / V_cruise
        partials['DOC', 'V_cruise'] = -C_time * (R / V_cruise**2)
        partials['DOC', 'SFC_tech'] = k_acq * C_eng_ref * (beta_base * delta_beta)

        partials['DOC', 'Cf_base'] = delta_Cf * m_fuel
        partials['DOC', 'C_time'] = R / V_cruise
        partials['DOC', 'k_acq'] = C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
        partials['DOC', 'C_eng_ref'] = k_acq * (1 + beta_base * delta_beta * SFC_tech)
        partials['DOC', 'beta_base'] = (k_acq * C_eng_ref) * (delta_beta * SFC_tech)