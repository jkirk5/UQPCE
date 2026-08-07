import openmdao.api as om
import unittest
from disciplines.propulsion import PropulsionComp
from openmdao.utils.assert_utils import assert_check_partials

class prop_test(unittest.TestCase):
    def test_partials(self):
        vector_size=1

        inputs = {
            'V_cruise':(240.5, 'm/s'), 'SFC_tech':(1.0, 'unitless'),
            'SFC_ref':(1.6e-4, '1/s'), 'V_ref':(231.5, 'm/s'),
            'eta_base':(0.4, 'unitless'), 'kv_base':(601.0, 'unitless'),
            'delta_eta':(1.0, 'unitless'), 'delta_kv':(1.0, 'unitless')
        }

        prob = om.Problem()
        prob.model.add_subsystem(
            'Prop', 
            PropulsionComp(vec_size=vector_size),
            promotes_inputs=['V_cruise', 'SFC_tech',
                             'SFC_ref', 'V_ref',
                             'eta_base', 'kv_base',
                             'delta_eta', 'delta_kv'],
            promotes_outputs=['SFC']
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