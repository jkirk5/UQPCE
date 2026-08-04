import openmdao.api as om
import numpy as np
from fixed import parameters

class Dpm(om.ExplicitComponent):
    """
    Component for normalized DOC containing analytical derivatives
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
        self.add_input('N_pax', val=parameters['N_pax'], units='unitless')

        #outputs
        self.add_output('Dpm', shape=(n,))

    def setup_partials(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.declare_partials('Dpm', ['N_pax'])
        self.declare_partials('Dpm', ['R', 'DOC'], rows=arange, cols=arange)

    def compute(self, inputs, outputs):

        N_pax = inputs['N_pax']
        DOC = inputs['DOC']
        R = inputs['R']

        outputs['Dpm'] = DOC / (N_pax * R)
    
    def compute_partials(self, inputs, partials):
        N_pax = inputs['N_pax']
        DOC = inputs['DOC']
        R = inputs['R']

        partials['Dpm', 'R'] = -(DOC / (N_pax * R**2))
        partials['Dpm', 'N_pax'] = -(DOC / (N_pax**2 * R))
        partials['Dpm', 'DOC'] = 1 / (N_pax * R)
        