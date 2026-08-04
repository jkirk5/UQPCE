import openmdao.api as om
import unittest
from disciplines.total_mass_comp import TotalMassComp
from openmdao.utils.assert_utils import assert_check_partials

class prop_test(unittest.TestCase):
    def test_partials(self):
        vector_size=1

        inputs = {
            'm_empty':(55000.0, 'kg'), 'm_fuel':(16000.0, 'kg'), 'm_payload':(17955.0, 'kg')
        }

        prob = om.Problem()
        prob.model.add_subsystem(
            'Mass', TotalMassComp(vec_size=vector_size),
            promotes_inputs=['m_empty', 'm_fuel', 'm_payload'],
            promotes_outputs=['m_total']
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