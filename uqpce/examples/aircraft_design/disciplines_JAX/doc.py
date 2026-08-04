import openmdao.api as om
import jax.numpy as jnp
from fixed import parameters

class DOC(om.JaxExplicitComponent):
    """
    Component for "DOCComp" box containing JAX
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
        self.add_input('delta_Cf', val=jnp.ones(n), units="unitless", shape=(n,))
        self.add_input('delta_beta', val=jnp.ones(n), units="unitless", shape=(n,))

        #tuning parameters
        self.add_input('Cf_base', units='USD/kg')
        self.add_input('beta_base', units="unitless")
        
        #constant parameters
        self.add_input('C_time', val=parameters['C_time'], units='USD/s')
        self.add_input('k_acq', val=parameters['k_acq'], units="unitless")
        self.add_input('C_eng_ref', val=parameters['C_eng_ref'], units='USD')

        #outputs
        self.add_output('DOC', units='USD', shape=(n,))
       
    def compute_primal(self, SFC_tech, V_cruise, R, m_fuel, delta_Cf, delta_beta, Cf_base, beta_base, C_time, k_acq, C_eng_ref):
        """
        DOC = Cf_base * delta_Cf * m_fuel + C_time * (R / V_cruise) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)
        """

        return Cf_base * delta_Cf * m_fuel + C_time * (R/V_cruise) + k_acq * C_eng_ref * (1 + beta_base * delta_beta * SFC_tech)