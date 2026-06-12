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
class AeroDicipline(om.ExplicitComponent):

    def setup(self):
    #Inputs-start~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #environemental inputs
        self.add_input('g', val=9.81, desc="Coefficient of Gravitational Acceleration [m/s^2]")
        self.add_input('rho', val=1.225, desc="Air Density [kg/m^3]")
        #baseline inputs and stuff 
        self.add_input('C_D0_base', val=0.03, desc="Baseline Drag Coefficient")
        self.add_input('S_0', val=125.0, desc="Baseline Planform Area [m^2]")
        self.add_input('ks_base',val=0.5, desc="Drag amplification factor [per unit area]")
        self.add_input('e_base', val=0.8,desc="Oswald Efficiency Factor")
        
        #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
        #design variable inputs
        self.add_input('S',val=125.0,desc="Planform Area [m^2]")
        self.add_input('V',val=100.0,desc="Cruising Free-stream Velocity [m/s]")
        self.add_input('AR',val=7.0,desc="Aspect Ratio of Planform")
        #I assume the value here will become the initial guess when selected as design variables 
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\/\/\/\/\/\/\/\/\/\/\/\/\/\//\//\/\/\/\

        #coupled solver inputs? not sure how this will be handled, I assume just 
        #treat like regular input for now?
        self.add_input('m_total',val=50000.0,desc="Total Mass [kg]")

        self.add_input('delta_CD0',val=1.0,desc="placeholder var for drag coeff uncertainty until we figure it out and what not")
        #in future do we replacde with a vector containing points on the normal distribution?
        self.add_input('delta_ks',val=1.0,desc="placeholder var for drag factor uncertainty until we figure it out and what not")
        self.add_input('delta_e',val=1.0,desc="placeholder var for oswald uncertainty until we figure it out and what not")
    #Inputs-end~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #outputs-start~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.add_output('CL',0.0,desc="Lift Coefficient of Configuration")
        self.add_output('CD',0.0,desc="Drag Coefficient of Configuration")
        self.add_output('LD',0.0,desc="Lift to Drag Ratio of Configuration")
    #outputs-end~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
    def setup_partials(self):
    #Sensitivities-start~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.declare_partials(of="CL",wrt="V",method="exact")
        self.declare_partials(of="CL",wrt="S",method="exact")
        self.declare_partials(of="CL",wrt="AR",method="exact")
        self.declare_partials(of="CL",wrt="m_total",method="exact")
        self.declare_partials(of="CL",wrt="rho",method="exact")

        self.declare_partials(of="CD",wrt="V",method="exact")
        self.declare_partials(of="CD",wrt="S",method="exact")
        self.declare_partials(of="CD",wrt="AR",method="exact")
        self.declare_partials(of="CD",wrt="m_total",method="exact")
        self.declare_partials(of="CD",wrt="rho",method="exact")

        self.declare_partials(of="LD",wrt="V",method="exact")
        self.declare_partials(of="LD",wrt="S",method="exact")
        self.declare_partials(of="LD",wrt="AR",method="exact")
        self.declare_partials(of="LD",wrt="m_total",method="exact")
        self.declare_partials(of="LD",wrt="rho",method="exact")

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
        partials['CL','AR'] = dCLdAR = 0 #fixed to assume S and AR as independent. span is always 
        #computed from these inputs
        partials['CL','m_total'] = dCLdm = CL/inputs['m_total']
        partials['CL','rho'] = dCLdrho = -CL/rho
    
        #ugliness helpers
        dCD_0dV = 0
        dCD_0dS = ks_base*delta_ks
        #b_squared = inputs['AR']*inputs['S']
        dSdAR = 0 #fixed to assume S and AR as independent. span is always 
        #computed from these inputs
        dCD_0dAR = dCD_0dS*dSdAR
        dARdS = 0 #fixed to assume S and AR as independent. span is always 
        #computed from these inputs
        dCD_0dm = 0
        dCD_0drho = 0 

        #product rule/quotient rule or whatever u wanna call it helpers
        product_rule_V = 2*CL*dCLdV*(1/inputs['AR']) #+ (CL**2)*(0)
        product_rule_S = 2*CL*dCLdS*(1/inputs['AR']) - (CL**2)*(1.0/(inputs['AR']**2))*dARdS
        product_rule_AR = 2*CL*dCLdAR*(1/inputs['AR']) - (CL**2)*(1.0/(inputs['AR']**2))*(1.0)
        product_rule_m = 2*CL*dCLdm*(1/inputs['AR'])
        product_rule_rho = 2*CL*dCLdrho*(1/inputs['AR'])
        
        partials['CD','V'] = dCDdV = dCD_0dV + (1/(np.pi*e_base*delta_e))*(product_rule_V)
        partials['CD','S'] = dCDdS =  dCD_0dS + (1/(np.pi*e_base*delta_e))*(product_rule_S)
        partials['CD','AR'] = dCDdAR = dCD_0dAR +  (1/(np.pi*e_base*delta_e))*(product_rule_AR)
        partials['CD','m_total'] = dCDdm =  dCD_0dm + (1/(np.pi*e_base*delta_e))*(product_rule_m)
        partials['CD','rho'] = dCDdrho =  dCD_0drho + (1/(np.pi*e_base*delta_e))*(product_rule_rho)

        partials['LD','V'] = (CD*dCLdV - CL*dCDdV)/(CD**2) 
        partials['LD','S'] = (CD*dCLdS - CL*dCDdS)/(CD**2)
        partials['LD','AR'] = (CD*dCLdAR - CL*dCDdAR)/(CD**2)
        partials['LD','m_total'] = (CD*dCLdm - CL*dCDdm)/(CD**2)
        partials['LD','rho'] = (CD*dCLdrho - CL*dCDdrho)/(CD**2)

def main():

    print("helloe")

if __name__ == "__main__":
    main()