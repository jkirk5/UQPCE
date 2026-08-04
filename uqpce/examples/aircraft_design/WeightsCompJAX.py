import openmdao.api as om
import jax.numpy as jnp

from fixed import parameters


class Weights_Struct(om.JaxExplicitComponent):
    """
    Evaluates the weights & structures for a coupled Breguet range with MDAO & JAX
    
    Inputs:
    Design Vars: S [m^2], AR [-], V [m/s]
    Vector coupling inputs: m_total [kg], m_engine [kg]
    Vector uncertain inputs: delta_kw, delta_fsys, delta_p
    Fixed parameters: kw_base, fsys_base, p_base, V_ref [m/s], m_fuse [kg]

    Outputs:
    Vectors: m_empty [kg], m_wing [kg]
    """

    def initialize(self):
        self.options.declare("vec_size", types=int)

    def setup(self):
        n = self.options["vec_size"]

        self.add_input("S", val=parameters["S_naught"], units="m**2")
        self.add_input("AR", val=parameters["b"] ** 2 / parameters["S_naught"])
        self.add_input("V", val=parameters["V_ref"], units="m/s")

        self.add_input("m_total", val=50000.0, shape=(n,), units="kg")
        self.add_input("m_engine", val=parameters["m_eng_ref"], shape=(n,), units="kg")

        self.add_input("delta_kw", val=1.0, shape=(n,))
        self.add_input("delta_fsys", val=1.0, shape=(n,))
        self.add_input("delta_p", val=1.0, shape=(n,))

        self.add_input("kw_base", val=parameters["kw_base"])
        self.add_input("fsys_base", val=parameters["fsys_base"])
        self.add_input("p_base", val=parameters["p_base"])
        self.add_input("V_ref", val=parameters["V_ref"], units="m/s")
        self.add_input("m_fuse", val=parameters["m_fuse"], units="kg")

        self.add_output("m_empty", val=0.0, shape=(n,), units="kg")
        self.add_output("m_wing", val=0.0, shape=(n,), units="kg")

    def compute_primal(
        self,
        S,
        AR,
        V,
        m_total,
        m_engine,
        delta_kw,
        delta_fsys,
        delta_p,
        kw_base,
        fsys_base,
        p_base,
        V_ref,
        m_fuse):
        
        m_wing = (kw_base * delta_kw * S**0.758 * AR**0.6 * m_total**0.006 * (V / V_ref) ** (p_base * delta_p))

        m_empty = (m_wing + m_fuse + fsys_base * m_total * delta_fsys + m_engine)

        return m_empty, m_wing