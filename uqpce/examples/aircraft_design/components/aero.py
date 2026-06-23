import numpy as np
import openmdao.api as om

#dtermined inputs
#planform area (S)
# Aspect Ratio (AR)
# Crusie Speed (V_cruise)

#coupled inputs
# m_total

#uncertain inputs (aleatory, I think)
# delta_CD0, delta_ks, delta_e

#outputs 
# LD, CL, CD

from fixed import parameters

class AeroDicipline(om.ExplicitComponent):

    def initialize(self):
        self.options.declare('vec_size', types=int)

    def setup(self):
        n = self.options['vec_size']
        arange = np.arange(n)
    #Inputs-start~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #environemental inputs
        self.add_input('g', val=9.81,units="m/s**2" ,desc="Coefficient of Gravitational Acceleration [m/s^2]")
        self.add_input('rho', val=0.38,units="kg/m**3" ,desc="Air Density [kg/m^3]")
        #baseline inputs and stuff 
        self.add_input('C_D0_base', val=parameters['CD0_base'], desc="Baseline Drag Coefficient")
        self.add_input('S_0',val=parameters['S_naught'],units="m**2" , desc="Baseline Planform Area [m^2]")
        self.add_input('ks_base',val=parameters['ks_base'],units="1/m**2", desc="Drag amplification factor [per unit area]")
        self.add_input('e_base', val=parameters['e_oswald_base'],desc="Oswald Efficiency Factor")
        
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #design variable inputs
        self.add_input('S',val=parameters['S_naught'],units="m**2",desc="Planform Area [m^2]")
        self.add_input('V',val=parameters['S_naught'],units="m/s",desc="Cruising Free-stream Velocity [m/s]")
        self.add_input('AR',val=7.0,desc="Aspect Ratio of Planform")
        #I assume the value here will become the initial guess when selected as design variables 
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\/\/\/\/\/\/\/\/\/\/\/\/\/\//\//\/\/\/\

        #coupled solver inputs? not sure how this will be handled, I assume just 
        #treat like regular input for now?
        self.add_input('m_total',val=50000.0,units="kg",desc="Total Mass [kg]")

        self.add_input('delta_CD0',val=1.0,shape=(n,),desc="placeholder var for drag coeff uncertainty until we figure it out and what not")
        #in future do we replacde with a vector containing points on the normal distribution?
        self.add_input('delta_ks',val=1.0,shape=(n,),desc="placeholder var for drag factor uncertainty until we figure it out and what not")
        self.add_input('delta_e',val=1.0,shape=(n,),desc="placeholder var for oswald uncertainty until we figure it out and what not")
    #Inputs-end~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #outputs-start~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.add_output('CL',0.0,desc="Lift Coefficient of Configuration")
        self.add_output('CD',0.0,shape=(n,),desc="Drag Coefficient of Configuration")
        self.add_output('LD',0.0,shape=(n,),desc="Lift to Drag Ratio of Configuration")
    #outputs-end~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
    def setup_partials(self):
    #Sensitivities-start~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.declare_partials(of="CL",wrt="V",method="exact")
        self.declare_partials(of="CL",wrt="S",method="exact")
        #self.declare_partials(of="CL",wrt="AR",method="exact")
        #des variables^
        self.declare_partials(of="CL",wrt="m_total",method="exact")
        self.declare_partials(of="CL",wrt="rho",method="exact")
        self.declare_partials(of="CL",wrt="g",method="exact")
        #all the rest of CL wrt other inputs are zero by default, so not needed
        #other partials just in case^

        self.declare_partials(of="CD",wrt="V",method="exact")
        self.declare_partials(of="CD",wrt="S",method="exact")
        self.declare_partials(of="CD",wrt="AR",method="exact")
        self.declare_partials(of="CD",wrt="m_total",method="exact")
        self.declare_partials(of="CD",wrt="rho",method="exact")
        self.declare_partials(of="CD",wrt="g",method="exact")
        self.declare_partials(of="CD",wrt="C_D0_base",method="exact")
        self.declare_partials(of="CD",wrt="S_0",method="exact")
        self.declare_partials(of="CD",wrt="e_base",method="exact")
        self.declare_partials(of="CD",wrt="delta_CD0",method="exact")
        self.declare_partials(of="CD",wrt="delta_e",method="exact")
        self.declare_partials(of="CD",wrt="ks_base",method="exact")
        self.declare_partials(of="CD",wrt="delta_ks",method="exact")


        self.declare_partials(of="LD",wrt="V",method="exact")
        self.declare_partials(of="LD",wrt="S",method="exact")
        self.declare_partials(of="LD",wrt="AR",method="exact")
        self.declare_partials(of="LD",wrt="m_total",method="exact")
        self.declare_partials(of="LD",wrt="rho",method="exact")
        self.declare_partials(of="LD",wrt="g",method="exact")
        self.declare_partials(of="LD",wrt="C_D0_base",method="exact")
        self.declare_partials(of="LD",wrt="S_0",method="exact")
        self.declare_partials(of="LD",wrt="e_base",method="exact")
        self.declare_partials(of="LD",wrt="delta_CD0",method="exact")
        self.declare_partials(of="LD",wrt="delta_e",method="exact")
        self.declare_partials(of="LD",wrt="ks_base",method="exact")
        self.declare_partials(of="LD",wrt="delta_ks",method="exact")

       


    #Sensitivities-end~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #passes input member inherited from om.Exp for reading and
    #outputs memeber struct/map thing whatever python calls it for writing
    def compute(self,inputs,outputs):
        g = inputs['g']
        rho = inputs['rho']
        C_D0_base = inputs['C_D0_base']
        S_0 = inputs['S_0']
        ks_base = inputs['ks_base']
        e_base = inputs['e_base']
        delta_CD0 = inputs['delta_CD0']
        delta_ks = inputs['delta_ks']
        delta_e = inputs['delta_e']


        #do this \/ double equal thingy to reuse output when needed, this synatx pattern might be useful
        #in compute partials function for chain rule stuff
        outputs['CL'] = CL = (inputs['m_total']*g) / ((1.0/2.0)*rho*(inputs['V']**2)*inputs['S'])
        C_D0 = C_D0_base*delta_CD0 + ks_base*delta_ks*(inputs['S']-S_0)     
        outputs['CD'] = CD = C_D0 + (CL**2) / (np.pi*inputs['AR']*e_base*delta_e)
        outputs['LD'] = CL/CD


    def compute_partials(self, inputs, partials): #I presume inputs and partials are inherited memebers of
        g = inputs['g']
        rho = inputs['rho']
        C_D0_base = inputs['C_D0_base']
        S_0 = inputs['S_0']
        ks_base = inputs['ks_base']
        e_base = inputs['e_base']
        delta_CD0 = inputs['delta_CD0']
        delta_ks = inputs['delta_ks']
        delta_e = inputs['delta_e']

        CL = (inputs['m_total']*g) / ((1.0/2.0)*rho*(inputs['V']**2)*inputs['S'])         
        C_D0 = C_D0_base*delta_CD0 + ks_base*delta_ks*(inputs['S']-S_0) 
        CD = C_D0 + (CL**2) / (np.pi*inputs['AR']*e_base*delta_e)
                                                  
        partials['CL','V'] = dCLdV = -2*CL*(1.0/inputs['V'])
        partials['CL','S'] = dCLdS = -1*CL*(1.0/inputs['S'])
        #partials['CL','AR'] = dCLdAR = 0 #fixed to assume S and AR as independent. span is always 
        #computed from these inputs
        dCLdAR = 0
        partials['CL','m_total'] = dCLdm = CL/inputs['m_total']
        partials['CL','rho'] = dCLdrho = -CL/rho
        partials['CL','g'] = dCLdg = CL/g
    
        #ugliness helpers
        dCD_0dV = 0.0
        dCD_0dS = ks_base*delta_ks
        #b_squared = inputs['AR']*inputs['S']
        dSdAR = 0.0 #fixed to assume S and AR as independent. span is always 
        #computed from these inputs
        dCD_0dAR = dCD_0dS*dSdAR
        dARdS = 0.0 #fixed to assume S and AR as independent. span is always 
        #computed from these inputs
        dCD_0dm = 0.0
        dCD_0drho = 0.0 
        dCD_0dg = 0.0
        #dARdg = 0.0
        dCD_0dCDbase = delta_CD0
        dCD_0dS0 = -ks_base*delta_ks
        dCD_0debase = 0.0
        dCD_0ddeltaCD0 = C_D0_base
        dCD_0ddeltae = 0


        #product rule/quotient rule or whatever u wanna call it helpers
        product_rule_V = 2*CL*dCLdV*(1/inputs['AR']) #+ (CL**2)*(0)
        product_rule_S = 2*CL*dCLdS*(1/inputs['AR']) - (CL**2)*(1.0/(inputs['AR']**2))*dARdS
        product_rule_AR = 2*CL*dCLdAR*(1/inputs['AR']) - (CL**2)*(1.0/(inputs['AR']**2))*(1.0)
        product_rule_m = 2*CL*dCLdm*(1/inputs['AR'])
        product_rule_rho = 2*CL*dCLdrho*(1/inputs['AR'])
        product_rule_g = 2*CL*dCLdg*(1/inputs['AR'])
        
        partials['CD','V'] = dCDdV = dCD_0dV + (1/(np.pi*e_base*delta_e))*(product_rule_V)
        partials['CD','S'] = dCDdS =  dCD_0dS + (1/(np.pi*e_base*delta_e))*(product_rule_S)
        partials['CD','AR'] = dCDdAR = dCD_0dAR +  (1/(np.pi*e_base*delta_e))*(product_rule_AR)
        partials['CD','m_total'] = dCDdm =  dCD_0dm + (1/(np.pi*e_base*delta_e))*(product_rule_m)
        partials['CD','rho'] = dCDdrho =  dCD_0drho + (1/(np.pi*e_base*delta_e))*(product_rule_rho)
        partials['CD','g'] = dCDdg =  dCD_0dg + (1/(np.pi*e_base*delta_e))*(product_rule_g)

        partials['CD','C_D0_base'] = dCDdCD0base =  dCD_0dCDbase 
        partials['CD','S_0'] = dCDdS0 =  dCD_0dS0 
        partials['CD','e_base'] = dCDdebase =  dCD_0debase - ((CL**2)/(np.pi*e_base*e_base*delta_e*inputs['AR']))
        partials['CD','delta_CD0'] = dCDddeltaCD0 =  dCD_0ddeltaCD0 
        partials['CD','delta_e'] = dCDddeltae =  dCD_0ddeltae - ((CL**2)/(np.pi*e_base*delta_e*delta_e*inputs['AR']))
        partials['CD','ks_base'] = dCDdks_base = delta_ks*(inputs['S']-S_0)
        partials['CD','delta_ks'] = dCDddelta_ks =  ks_base*(inputs['S']-S_0)

        partials['LD','V'] = (CD*dCLdV - CL*dCDdV)/(CD**2) 
        partials['LD','S'] = (CD*dCLdS - CL*dCDdS)/(CD**2)
        partials['LD','AR'] = (CD*dCLdAR - CL*dCDdAR)/(CD**2)
        partials['LD','m_total'] = (CD*dCLdm - CL*dCDdm)/(CD**2)
        partials['LD','rho'] = (CD*dCLdrho - CL*dCDdrho)/(CD**2)
        partials['LD','g'] = (CD*dCLdg - CL*dCDdg)/(CD**2)

        partials['LD','C_D0_base'] =  (0 - CL*dCDdCD0base)/(CD**2) 
        partials['LD','S_0'] = (0 - CL*dCDdS0)/(CD**2) 
        partials['LD','e_base'] = (0 - CL*dCDdebase)/(CD**2) 
        partials['LD','delta_CD0'] = (0 - CL*dCDddeltaCD0)/(CD**2) 
        partials['LD','delta_e'] = (0 - CL*dCDddeltae)/(CD**2) 
        partials['LD','ks_base'] = -(CL*dCDdks_base)/(CD**2)
        partials['LD','delta_ks'] = -(CL*dCDddelta_ks)/(CD**2)

import unittest
from openmdao.utils.assert_utils import assert_check_partials

class TestAero(unittest.TestCase):

    #inherits mnethods like:
    #self.assertEqual() et cetera

    #I guess this framework uses this name convention
    #runs before every func that starts with test__
    def setUp(self):
        self.prob = om.Problem()
        
        #dummy model to test aero
        self.prob.model.add_subsystem('Aero',AeroDicipline(),promotes=['*'])
        #promotes makes sure evrything is accesible at self level
        #runs after every, individual, function that starts with test__
        #i guess its used to reset state of object being tested if needed

        self.prob.setup(force_alloc_complex=True)
        
        self.prob.set_val('m_total', 73229.6)
        self.prob.set_val('g', 9.80665)
        self.prob.set_val('rho', 0.38)
        self.prob.set_val('V', 230.0)
        self.prob.set_val('S', 102.0)
        self.prob.set_val('AR', 9.0)

        self.prob.set_val('C_D0_base', 0.02)
        self.prob.set_val('ks_base', 0.0005)
        self.prob.set_val('S_0', 100.0)
        self.prob.set_val('e_base', 0.8)

        self.prob.set_val('delta_CD0', 1.0)
        self.prob.set_val('delta_ks', 1.0)
        self.prob.set_val('delta_e', 1.0)

        self.prob.run_model()

    def tearDown(self):
        pass #does nothing 

    def test_partials(self):
        partial_data = self.prob.check_partials(method='cs')
        assert_check_partials(partial_data, atol=1e-12, rtol=1e-12)

    def test_bahavior(self):
        m_total = self.prob.get_val('m_total')
        g = self.prob.get_val('g')
        rho = self.prob.get_val('rho')
        V = self.prob.get_val('V')
        S = self.prob.get_val('S')

        expected_CL = (m_total * g) / (0.5 * rho * V**2 * S)
        actual_CL = self.prob.get_val('CL')

        np.testing.assert_allclose(actual_CL, expected_CL, rtol=1e-12, atol=1e-12)

        AR = self.prob.get_val('AR')

        C_D0_base = self.prob.get_val('C_D0_base')
        S_0 = self.prob.get_val('S_0')
        ks_base = self.prob.get_val('ks_base')
        e_base = self.prob.get_val('e_base')

        delta_CD0 = self.prob.get_val('delta_CD0')
        delta_ks = self.prob.get_val('delta_ks')
        delta_e = self.prob.get_val('delta_e')

        CL = (m_total * g) / (0.5 * rho * V**2 * S)

        C_D0 = C_D0_base * delta_CD0 + ks_base * delta_ks * (S - S_0)

        expected_CD = C_D0 + (CL**2) / (np.pi * AR * e_base * delta_e)
        actual_CD = self.prob.get_val('CD')

        np.testing.assert_allclose(actual_CD, expected_CD, rtol=1e-12, atol=1e-12)

        LoD = self.prob.get_val('LD')

        expected_LoD = CL/expected_CD
        np.testing.assert_allclose(LoD, expected_LoD, rtol=1e-12, atol=1e-12)

def main():

    test = TestAero()
    test.setUp()
    test.test_partials()
    test.test_bahavior()

if __name__ == "__main__":
    main()