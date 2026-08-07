import openmdao.api as om
import unittest
from disciplines.weight import EngineWeightComp
from openmdao.utils.assert_utils import assert_check_partials

class prop_test(unittest.TestCase):
    def test_partials(self):
        vector_size=1

        inputs = {
            'SFC_tech':(1.0, 'unitless'),
            'm_eng_ref':(8602.0, 'kg'), 'alpha_base':(0.345, 'unitless'),
            'delta_alpha':(1.0, 'unitless')
        }

        prob = om.Problem()
        prob.model.add_subsystem(
            'Engine', 
            EngineWeightComp(vec_size=vector_size), 
            promotes_inputs=['SFC_tech', 
                             'm_eng_ref', 'alpha_base',
                             'delta_alpha'],
            promotes_outputs=['m_engine']
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