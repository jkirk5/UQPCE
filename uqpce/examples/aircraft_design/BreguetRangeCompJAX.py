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

        self.add_input("V", val=parameters["V_ref"], units="m/s")
        self.add_input("SFC", val=parameters["SFC_ref"], shape=(n,), units="1/s")
        self.add_input("LD", val=16.0, shape=(n,))

        self.add_input("m_total", val=50000.0, shape=(n,), units="kg")
        self.add_input("m_fuel", val=10000.0, shape=(n,), units="kg")

        self.add_output("R", val=1.0e6, shape=(n,), units="m")

    def compute_primal(self, V, SFC, LD, m_total, m_fuel):
        return ((V / SFC) * LD * jnp.log(m_total / (m_total - m_fuel)))