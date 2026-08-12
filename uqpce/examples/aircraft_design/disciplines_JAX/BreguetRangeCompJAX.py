import openmdao.api as om
import jax.numpy as jnp

from fixed import parameters


class BreguetRangeComp(om.JaxExplicitComponent):
    """
    Compute Breguet range from fuel mass using JAX

    Inputs:
    Design Varibale: V_cruise [m/s]
    Vector inputs (UQ): SFC [1/s], LD [], m_total [kg], m_fuel [kg]

    Outputs:
    Vector output: R [m]
    """

    def initialize(self):
        self.options.declare("vec_size", types=int)

    def setup(self):
        n = self.options["vec_size"]

        self.add_input("V_cruise", units="m/s")
        self.add_input("SFC", shape=(n,), units="1/s")
        self.add_input("LD", shape=(n,), units="unitless")

        self.add_input("m_total", shape=(n,), units="kg")
        self.add_input("m_fuel", shape=(n,), units="kg")

        self.add_output("R", shape=(n,), units="m")

    def compute_primal(self, V_cruise, SFC, LD, m_total, m_fuel):
        return ((V_cruise / SFC) * LD * jnp.log(m_total / (m_total - m_fuel)))