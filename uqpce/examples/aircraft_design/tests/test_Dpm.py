import openmdao.api as om
import unittest
from disciplines.dpm import Dpm
from openmdao.utils.assert_utils import assert_check_partials

class prop_test(unittest.TestCase):
    def test_partials(self):
        vector_size=1

        inputs = {
            'DOC':(60000, 'USD'), 'R':(5.5e3, 'km'), 'N_pax':(189.0, 'unitless')
        }

        prob = om.Problem()
        prob.model.add_subsystem(
            'DPM_objective', 
            Dpm(vec_size=vector_size), 
            promotes_inputs=['DOC', 'R', 'N_pax'], 
            promotes_outputs=['Dpm']
        )

        prob.setup(force_alloc_complex=True)

        for input in inputs:
            val = inputs[input][0]
            units = inputs[input][1]
            prob.model.set_val(input, val, units)

        partial_data = prob.check_partials(out_stream=None, method='cs')
        assert_check_partials(partial_data, atol=1e-12, rtol=1e-12)

if __name__ == '__main__':
    unittest.main()