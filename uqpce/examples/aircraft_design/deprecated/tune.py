import numpy as np
from scipy.optimize import minimize

import openmdao.api as om

from disciplines.objective import *
from disciplines.BreguetRange import *
from disciplines.aero import *
from disciplines.total_mass_comp import *
from uqpce.examples.aircraft_design.disciplines.propulsion import *
from disciplines.weight import *

from fixed import parameters
from helpers import initialize_og
from deprecated.optimize import CoupledGroup


TUNING_NAMES = [
    'aircraft.Weight.p_base',
    'aircraft.Prop.eta_base',
    'aircraft.Prop.kv_base',
    'aircraft.Engine.alpha_base',
    'aircraft.DOC.beta_base',
    'aircraft.Aero.ks_base',
]


def build_inner_problem():
    prob = om.Problem(reports=False)
    prob.model.add_subsystem('aircraft', CoupledGroup(), promotes=['*'])

    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'SLSQP'
    prob.driver.options['maxiter'] = 100
    prob.driver.options['tol'] = 1e-8
    prob.driver.options['disp'] = False

    # Inner design optimization: aircraft variables
    prob.model.add_design_var('S', lower=100.0, upper=180.0, ref=parameters['S'])
    prob.model.add_design_var('AR', lower=7.0, upper=50.0, ref=parameters['AR'])
    prob.model.add_design_var('V', lower=200.0, upper=260.0, ref=parameters['V'])
    prob.model.add_design_var('SFC_tech', lower=-1.0, upper=1.0, ref=1.0)

    # Inner objective: normal aircraft optimization
    prob.model.add_objective('aircraft.DOC.DOC', ref=1.0e4)

    prob.model.add_constraint(
        'aircraft.Balance.m_fuel',
        lower=1000.0,
        upper=50000.0,
        ref=16000.0
    )

    prob.model.add_constraint(
        'aircraft.Aero.CL',
        lower=0.4,
        upper=0.53,
        ref=0.5
    )

    prob.setup()
    initialize_og(prob)

    return prob


def calibration_objective(x):
    prob = build_inner_problem()

    for name, value in zip(TUNING_NAMES, x):
        prob.set_val(name, value)

    try:
        prob.run_driver()
    except Exception:
        return 1.0e12

    S = prob.get_val('S').item()
    AR = prob.get_val('AR').item()
    V = prob.get_val('V').item()
    SFC_tech = prob.get_val('SFC_tech').item()

    J = (
        ((AR - parameters['AR']) / parameters['AR']) ** 2
        + ((S - parameters['S']) / parameters['S']) ** 2
        + ((V - parameters['V']) / parameters['V']) ** 2
        + (SFC_tech-.35) ** 2
    )

    print(
        f"J={J:.6e}, "
        f"S={S:.3f}, AR={AR:.3f}, V={V:.3f}, SFC_tech={SFC_tech:.3f}, "
        f"x={x}"
    )

    return J


def main():
    x0 = np.array([
        tuning['p_base'],
        tuning['eta_base'],
        tuning['kv_base'],
        tuning['alpha_base'],
        tuning['beta_base'],
        tuning['ks_base'],
    ])

    bounds = [
        (0.01, 12.0),       # p_base
        (0.1, 0.3),        # eta_base
        (30, 100.0),       # kv_base
        (0.1, 0.3),        # alpha_base
        (0.2, 0.5),        # beta_base
        (0.000001, 5.0e-3),     # ks_base
    ]

    result = minimize(
    calibration_objective,
    x0,
    method='COBYLA',
    bounds=bounds,
    options={
        'maxiter': 500,
        'xatol': 1e-4,
        'fatol': 1e-6,
        'disp': True,
        }
    )

    print("\nBest tuning parameters:")
    for name, value in zip(TUNING_NAMES, result.x):
        print(name, value)

    print("\nFinal calibration objective:", result.fun)


if __name__ == "__main__":
    main()