from fixed import parameters
import openmdao.api as om

#this can be done at the top level of heierarchy using balance comp
#but fuck it we ball
class TotalMass(om.ImplicitComponent):

    #in the quadratic formula example, the inputs are non implicit parameters
    #but in our case they are just known. the outputs, are actually psuedo inputs to the 
    #residual equation. by solving the residual equations, we get the outputs (i.e. inputs to thiose residuals)
    #that we need. in our model, no box gives m_total or m_fuel as an output,
    #so the implicit component must
    def setup(self):
        #known to the box
        self.add_input('V_cruise',val=100)
        self.add_input('SFC',val=0.7)
        self.add_input('L/D',val=5)
        self.add_input('m_empty',val=100000)
        self.add_input('m_fuse',val=parameters["m_fuse"])
        self.add_input('m_payload',val=parameters["m_fuse"])
        
        # THIS IS A STUPID CONSEQUENCE OF
        #MDAO SYNTAX. THE OUTPUT KEY AND 
        #RESIDUAL KEY, MUST BE THE SAME.
        self.add_output('m_fuel', val=30000)
        self.add_output('m_total')
    def setup_partials(self):

    
    def apply_nonlinear(self, inputs, outputs, residuals):


    def solve_nonlinear(self, inputs, outputs):
        
    def linearize(self, inputs, outputs, partials):



       