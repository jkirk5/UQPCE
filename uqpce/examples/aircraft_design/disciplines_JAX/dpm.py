import openmdao.api as om
import jax.numpy as jnp
from fixed import parameters

class Dpm(om.JaxExplicitComponent):
    """
    Component for normalized DOC containing JAX
    """
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']

        #proposed design variables
        #n/a

        #model variable (output from other component)
        self.add_input('DOC', units='USD', shape=(n,))
        self.add_input('R', units='km', shape=(n,))

        #uncertain parameters
        #n/a

        #tuning parameters
        #n/a

        #constant parameters
        self.add_input('N_pax', val=parameters['N_pax'])

        #outputs
        self.add_output('Dpm', shape=(n,))

    def compute_primal(self, DOC, R, N_pax):
        """
        Dpm = DOC / (pax * km)
        """

        return DOC / (N_pax * R)