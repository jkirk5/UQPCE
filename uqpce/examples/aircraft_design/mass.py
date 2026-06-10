from fixed import parameters
import openmdao.api as om
import numpy as np

#this can be done at the top level of heierarchy using balance comp
#but fuck it we ball

def range(SFC,V,LoverD,m_total,m_fuel):

    return (V/SFC)*(LoverD)*np.log((m_total)/(m_total-m_fuel))

class Residual(om.ImplicitComponent):

    #in the quadratic formula example, the inputs are non implicit parameters
    #but in our case they are just known. the outputs, are actually psuedo inputs to the 
    #residual equation. by solving the residual equations, we get the outputs (i.e. inputs to thiose residuals)
    #that we need. in our model, no box gives m_total or m_fuel as an output,
    #so the implicit component must
    def setup(self):
        #inputs
        self.add_input('V_cruise',val=100)
        self.add_input('SFC',val=0.7)
        self.add_input('L/D',val=5)
        self.add_input('m_empty',val=100000)
        #const inputs
        #self.add_input('m_fuse',val=parameters["m_fuse"])
        #self.add_input('m_payload',val=parameters["m_payload"])
        
        # THIS IS A STUPID CONSEQUENCE OF
        #MDAO SYNTAX. THE OUTPUT KEY AND 
        #RESIDUAL KEY, MUST BE THE SAME.
        self.add_output('m_total', val=100000)
        self.add_output('m_fuel',val=30000)


    def setup_partials(self):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
        #derivatives of residual one...
        #(Resid_1 = m_total - m_empty - m_pay - m_fuel = 0) 
        #to form row one of Jacobian
        self.declare_partials(of='m_total',wrt='m_total') #J11
        self.declare_partials(of='m_total',wrt='m_fuel') #J12
        #derivatives of residual two...
        # (Resid_2 = R - R_target = 0) 
        #to form row two of Jacobian
        self.declare_partials(of='m_fuel',wrt='m_total') #J21
        self.declare_partials(of='m_fuel',wrt='m_fuel') #J22
        #in my convention, the residual vector is...
        #Res = [Mass_residual, Range Residual]
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   

        #derivatives for optimizing
        self.declare_partials(of='m_total',wrt='V_cruise')
        self.declare_partials(of='m_total',wrt='SFC')
        self.declare_partials(of='m_total',wrt='L/D')
        self.declare_partials(of='m_total',wrt='m_empty')

        #derivatives for optimizing
        self.declare_partials(of='m_fuel',wrt='V_cruise')
        self.declare_partials(of='m_fuel',wrt='SFC')
        self.declare_partials(of='m_fuel',wrt='L/D')
        self.declare_partials(of='m_fuel',wrt='m_empty')

    def apply_nonlinear(self, inputs, outputs, residuals):
        #dead ass inputs
        V = inputs['V_cruise']
        SFC = inputs['SFC']
        LoverD = inputs['L/D']
        m_empty = inputs['m_empty']

        #outputs
        m_total = outputs['m_total']
        m_fuel = outputs['m_fuel']

        #const parameters
        m_payload = parameters['m_payload']
        R_target = parameters['R_target']

        #residual associated with m_total key
        residuals['m_total'] = m_total - m_empty - m_fuel - m_payload

        #residual associated with m_fuel key
        residuals['m_fuel'] = range(SFC,V,LoverD,m_total,m_fuel) - R_target


    #not always possible for equations that have no solution to the 
    #system formed by Resdiual_vector = zero_vector. But in our case there is one
    #so it will be provided here. I am pretty sure openMDAO will use this to close
    #the residual without newton iterations if provided, which basically turns
    #this into an explicit component, where the derivatives of m_fuel and 
    #m_total are computed using the derivatives of the residuals. regardless,
    #not all implicit components lend themselves to a solution, and rewriting
    #as explicit component may not be possible in most cases. It is good
    #practice for now though.
    def solve_nonlinear(self, inputs, outputs):
        V = inputs['V_cruise']
        SFC = inputs['SFC']
        LoverD = inputs['L/D']
        m_empty = inputs['m_empty']

        m_payload = parameters['m_payload']
        R_target = parameters['R_target']

        exp_term = np.exp(R_target*(SFC/V)*(1/LoverD))

        m_fuel = (m_empty + m_payload)/((-(exp_term)/(1-exp_term))-1)

        outputs['m_total'] = (-(exp_term)/(1-exp_term))*m_fuel
        outputs['m_fuel'] = m_fuel

        
    def linearize(self, inputs, outputs, partials):
        #dead ass inputs
        V = inputs['V_cruise']
        SFC = inputs['SFC']
        LoverD = inputs['L/D']
        m_empty = inputs['m_empty']

        #outputs
        m_total = outputs['m_total']
        m_fuel = outputs['m_fuel']

        #const parameters
        m_payload = parameters['m_payload']
        R_target = parameters['R_target']

        #\/\/\/\/ Jacobian population \/\/\/\/
        #row 1 ~ gradient of mass resdiual equation
        partials['m_total','m_total'] = J11 = 1
        partials['m_total','m_fuel'] = J12 = -1
        #row 2 ~ gradient of range residual equation
        fuel_mass_fraction = (m_total - m_fuel)/(m_total)
        partials['m_fuel','m_total'] = J21 = (V/SFC)*(LoverD)*fuel_mass_fraction*((-m_fuel)/((m_total-m_fuel)**2))
        partials['m_fuel','m_fuel'] = J22 = (V/SFC)*(LoverD)*fuel_mass_fraction*((m_total)/((m_total-m_fuel)**2))
        #/\/\/\/\ Jacobian population /\/\/\/\

        #other derivatives of residuals for 
        #optimization and derivative propagation
        # Mass residual derivatives
        partials['m_total','V_cruise'] = 0
        partials['m_total','SFC'] = 0
        partials['m_total','L/D'] = 0
        partials['m_total','m_empty'] = -1

        R = range(SFC,V,LoverD,m_total,m_fuel)
        #Range residual derivatives
        partials['m_fuel','V_cruise'] = R/V
        partials['m_fuel','SFC'] = -R/SFC
        partials['m_fuel','L/D'] = R/LoverD
        partials['m_fuel','m_empty'] = 0


        #declare a member variable to store jacobian and inverse jacobian like doc example
        #possibly useful for testing later?

        self.Jacobian = np.array([[J11,J12],
                                 [J21,J22]])
        
        det_J = J11*J22 - J12*J21

        self.inv_Jacobian = np.array([[J22,-J12],
                                 [-J21,J11]])






       