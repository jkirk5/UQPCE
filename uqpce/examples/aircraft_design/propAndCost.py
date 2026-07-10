import openmdao.api as om

class Propulsion(om.JaxExplicitComponent):
    """
    Component for "PropulsionComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']

        #Parameters
        self.add_input('SFC_ref', units='1/s', desc="Reference SFC technology factor")
        self.add_input('eta_base')
        self.add_input('kv_base')
        self.add_input('V_ref', val=231.5, units="m/s", desc="Reference flight speed")

        #Global design variables
        self.add_input('SFC_tech', val=0., desc="SFC technology factor")
        self.add_input('V', units='m/s', desc="Cruise speed")

        #Uncertainties
        self.add_input('delta_eta', val=1.0, shape=(n,))
        self.add_input('delta_kv', val=1.0, shape=(n,))

        #Output
        self.add_output('SFC', units="1/s", desc="Specific fuel consumption", shape=(n,))

    def compute_primal(self, SFC_ref, eta_base, kv_base, V_ref, SFC_tech, V, delta_eta, delta_kv):
        """
        SFC = SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (1 + kv_base * delta_kv * (V/V_ref - 1)^2)
        """

        return SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (1 + kv_base * delta_kv * (V/V_ref - 1)**2)
    
class EngineWeight(om.JaxExplicitComponent):
    """
    Component for "EngineWeightComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']

        #Parameters
        self.add_input('m_eng_ref', units='kg')
        self.add_input('alpha_base')

        #Global design variables
        self.add_input('SFC_tech', val=0., desc='SFC technology factor')
    
        #Uncertainties
        self.add_input('delta_alpha', val=1.0, shape=(n,))

        #Output
        self.add_output('m_engine', units='kg', desc='Engine mass', shape=(n,))

    def compute_primal(self, m_eng_ref, alpha_base, SFC_tech, delta_alpha):
        """
        m_engine = m_eng_ref * (1 + alpha_base * delta_alpha * SFC_tech)
        """
        
        return m_eng_ref * (1 + alpha_base * delta_alpha * SFC_tech)

class DOC(om.JaxExplicitComponent):
    """
    Component for "DOCComp" box containing analytical derivatives
    """
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']

        #Parameters
        self.add_input('Cf_base', units='USD/kg')
        self.add_input('C_time', units='USD/s')
        self.add_input('k_acq')
        self.add_input('C_eng_ref', units='USD')
        self.add_input('beta_base')

        #Global design variables
        self.add_input('SFC_tech', val=0., desc='SFC technology factor')
        self.add_input('V_cruise', units='m/s', desc='Cruise speed')

        #Local design variable
        self.add_input('R', units='m', desc='Breguet range', shape=(n,))
        
        #Solver state
        self.add_input('m_fuel', units='kg', desc='Fuel mass', shape=(n,)) 

        #Uncertainties
        self.add_input('delta_Cf', val=1.0, shape=(n,))
        self.add_input('delta_beta', val=1.0, shape=(n,))

        #Output
        self.add_output('DOC', units='USD', desc="Direct operating cost", shape=(n,))

    def compute_primal(self, Cf_base, C_time, k_acq, C_eng_ref, beta_base, SFC_tech, V_cruise, R, m_fuel, delta_Cf, delta_beta):
        """
        DOC = Cf_base * delta_Cf * m_fuel + C_time * (R / V_cruise) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
        """

        return Cf_base * delta_Cf * m_fuel + C_time * (R/V_cruise) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)

class Dpm(om.JaxExplicitComponent):
    """
    Component for objective of minimizing DOC/pax*km
    """
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']

        #Parameters
        self.add_input('DOC', units='USD', shape=(n,))

        self.add_input('N_pax', desc="Number of passengers")

        #Local design variable
        self.add_input('R', units='km', desc='Breguet range', shape=(n,))

        #Output
        self.add_output('Dpm', desc="DOC/pax*km", shape=(n,))

    def compute_primal(self, DOC, N_pax, R):
        """
        Dpm = DOC / (pax * km)
        """

        return DOC / (N_pax * R)