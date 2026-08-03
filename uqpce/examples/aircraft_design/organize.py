from disciplines.BreguetRange import *
from disciplines.aero import *
from disciplines.total_mass_comp import *
from disciplines.propAndCost import *
from disciplines.weight import *
from disciplines.objective import *
from disciplines.doc import *
from disciplines.dpm import *

#for julia stuff
import os
import openmdao.api as om
from juliacall import Main as jl
from omjlcomps import JuliaExplicitComp


class CoupledDisciplines(om.Group):

    def initialize(self):
        self.options.declare('vec_size',default=1, types=int)

    def setup(self):
        n = self.options['vec_size']

        ###Total Mass Component####################################
        self.add_subsystem(
            'Mass',TotalMassComp(vec_size=n),
            promotes_inputs=['m_empty',
                             'm_fuel'],
            promotes_outputs=['m_total']
                           )
        #^######################################################^#

        ###Breguet Range Component################################
        self.add_subsystem(
            'Range',BreguetRangeComp(vec_size=n),
            promotes_inputs=['V_cruise',
                            'm_total','LD',
                            'SFC',
                            'm_fuel'],
            promotes_outputs=['R']
                           )
        #^######################################################^#

        ###Structural Weight Component############################
        self.add_subsystem(
            'Weight',Weights_Struct(vec_size=n),
            promotes_inputs=['S','AR','V_cruise',
            'delta_kw','delta_fsys','delta_p',
            'm_total','m_engine'],
            promotes_outputs=['m_wing','m_empty']
                           )
        #^######################################################^#

        ###Aerodynamics Component#################################
        #self.add_subsystem(
        #    'Aero',AeroCompJax(vec_size=n),
        #    promotes_inputs=['S','AR','V_cruise',
        #    'delta_CD0','delta_ks','delta_e',
        #    'm_total'], 
        #    promotes_outputs=['CL','CD','LD','WL']
        #                   )
        #^######################################################^#

        #~~~ Temporary Julia Aero Comp ~~~~~~~~~~~~~~~~~~~~~~~~~~~
        jl.include(os.path.abspath(r"C:\Users\lkohler\Projects\MDAO\UQPCE\uqpce\examples\aircraft_design\disciplines\Julia\aero.jl"))
        jl_aero_comp = jl.AeroCompJulia.get_aero_comp(n)
        AeroCompJulia = JuliaExplicitComp(jlcomp=jl_aero_comp)
        self.add_subsystem(
                    'Aero',AeroCompJulia,
                    promotes_inputs=['S','AR','V_cruise',
                    'delta_CD0','delta_ks','delta_e',
                    'm_total'], 
                    promotes_outputs=['CL','CD','LD','WL']
                                   )
        #~~~ Temporary Julia Aero Comp ~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ###Range Residual#########################################
        initial_guess = np.ones(n)*16000 #kg
        Balance = om.BalanceComp()
        
        Balance.add_balance(
            name='m_fuel',val=initial_guess,
            units='kg',lower=1000.0,upper=50000.0,
            lhs_name='R',rhs_name='R_target',
            rhs_val=parameters['R_target'],
            eq_units='m',ref=16000.0,res_ref=1.0e6,
            )
        
        self.add_subsystem('Balance', Balance,
                           promotes_inputs=['R'],
                           promotes_outputs=['m_fuel'])
        #^######################################################^#
        
        ###Residual Solver Options################################
        newton = self.nonlinear_solver = om.NewtonSolver(solve_subsystems=True)
        self.nonlinear_solver.options['iprint'] = 2
        self.nonlinear_solver.options['maxiter'] = 500
        self.nonlinear_solver.options['atol'] = 1e-5
        self.nonlinear_solver.options['rtol'] = 1e-3

        line_search = newton.linesearch = om.ArmijoGoldsteinLS(
                                    bound_enforcement='vector',
                                        )
        line_search.options['maxiter'] = 20
        line_search.options['print_bound_enforce'] = True
        self.linear_solver = om.DirectSolver()
        #^######################################################^#

class ExampleMDA(om.Group):

    def initialize(self):
        self.options.declare('vec_size',default=1, types=int)
    
    def setup(self):
        n = self.options['vec_size']

        ###Propulsion Components##################################
        self.add_subsystem(
            'Prop', Propulsion(vec_size=n),
            promotes_inputs=['delta_eta','delta_kv',
                             'V_cruise','SFC_tech'],
            promotes_outputs=['SFC']
                          )
        #^######################################################^#

        ###Engine Weight Component################################
        self.add_subsystem(
            'Engine', EngineWeight(vec_size=n), 
            promotes_inputs=['delta_alpha','SFC_tech'],
            promotes_outputs=['m_engine']
                           )
        #^######################################################^#
        
        ###Coupled Component Group################################
        self.add_subsystem(
            'Coupled', CoupledDisciplines(vec_size=n), 
            promotes_inputs=['delta_kw','delta_fsys','delta_p',
                            'delta_CD0','delta_ks','delta_e',
                            'S','AR','V_cruise',
                            'SFC','m_engine'],
            promotes_outputs=['R',
                              'm_fuel','m_total',
                              'm_empty','m_wing',
                              'CL','CD','LD','WL']
                           )
        #^######################################################^#

class CL_constraint(om.ExplicitComponent):
    
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.add_input('CL', shape=(n,))

        self.add_input('CL_target', val=0.53)

        self.add_output('CL_constraint', shape=(n,))

        # should be identity matrix
        self.declare_partials('CL_constraint', 'CL', rows=arange, cols=arange)

    def compute(self, inputs, outputs):

        CL = inputs['CL']
        CL_target = inputs['CL_target']

        outputs['CL_constraint'] = CL_target - CL

    def compute_partials(self, inputs, partials):

        partials['CL_constraint', 'CL'] = -1

class WingLoad_constraint(om.ExplicitComponent):
    
    def initialize(self):
        self.options.declare('vec_size', default=1, types=int)

    def setup(self):
        n = self.options['vec_size']
        arange = np.arange(n)

        self.add_input('WL', shape=(n,))

        self.add_input('WL_target',val=5905.0)

        self.add_output('WL_constraint', shape=(n,))

        # should be identity matrix
        self.declare_partials('WL_constraint', 'WL', rows=arange, cols=arange)

    def compute(self, inputs, outputs):

        WL = inputs['WL']
        WL_target = inputs['WL_target']

        outputs['WL_constraint'] = WL_target - WL

    def compute_partials(self, inputs, partials):

        partials['WL_constraint', 'WL'] = 1

def configure_subsystems(prob,vector_size=1):

    prob.model.add_subsystem(
        'MDA', 
        ExampleMDA(vec_size=vector_size), 
        promotes_inputs=(['V_cruise', 'S', 'AR', 'SFC_tech',
                          'delta_eta', 'delta_kv','delta_alpha',
                          'delta_CD0','delta_ks','delta_e',
                          'delta_fsys','delta_kw','delta_p']), 
        promotes_outputs=['m_fuel','m_empty','m_engine',
                          'm_total','LD','CL','CD','WL','SFC','R']
    )

   # prob.model.add_subsystem(
   #     'WingLoad_constraint', 
   #     WingLoad_constraint(vec_size=vector_size), 
   #     promotes_inputs=['WL'], 
   #     promotes_outputs=['WL_constraint']
   # )

    prob.model.add_subsystem(
        'LiftCoeff_constraint', 
        CL_constraint(vec_size=vector_size), 
        promotes_inputs=['CL'], 
        promotes_outputs=['CL_constraint']
    )

    prob.model.add_subsystem(
        'DOC_objective', 
        DOC(vec_size=vector_size), 
        promotes_inputs=(['V_cruise','SFC_tech',
                          'delta_beta','delta_Cf','R','m_fuel']), 
        promotes_outputs=['DOC']
    )

    prob.model.add_subsystem(
        'DPM_objective', 
        Dpm(vec_size=vector_size), 
        promotes_inputs=['DOC','R'], 
        promotes_outputs=['Dpm']
    )
