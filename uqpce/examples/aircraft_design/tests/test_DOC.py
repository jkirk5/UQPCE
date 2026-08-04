import openmdao.api as om
import unittest
from disciplines.doc import DOC
from openmdao.utils.assert_utils import assert_check_partials

class prop_test(unittest.TestCase):
    def test_partials(self):
        vector_size=1

        inputs = {
            'V_cruise':(240.5, 'm/s'), 'SFC_tech':(1.0, 'unitless'),
            'Cf_base':(0.74, 'USD/kg'), 'beta_base':(0.55, 'unitless'),
            'C_time':(0.472, 'USD/s'), 'k_acq':(0.00142, 'unitless'), 'C_eng_ref':(2.2e7, 'USD'),
            'delta_beta':(1.0, 'unitless'), 'delta_Cf':(1.0, 'unitless'),
            'R':(5.5e6, 'm'), 'm_fuel':(16000, 'kg')
        }

        prob = om.Problem()
        prob.model.add_subsystem(
            'DOC_objective', 
            DOC(vec_size=vector_size), 
            promotes_inputs=['V_cruise', 'SFC_tech',
                             'Cf_base', 'beta_base',
                             'C_time', 'k_acq', 'C_eng_ref', 
                             'delta_beta', 'delta_Cf', 
                             'R', 'm_fuel'], 
            promotes_outputs=['DOC']
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