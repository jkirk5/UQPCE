parameters = {
    # Mission / payload
    # 737-800 max range is often quoted around 5,765 km.
    # If you want a more conservative full-payload airline range, use 4.8e6 instead.
    "R_target": 10e6,       # m
    "N_pax": 162,              # passengers, typical 2-class 737-800
    "m_payload": 16200.0,      # kg, approx 100 kg/passenger incl. bags

    # Propulsion
    # For your current Breguet formula:
    # R = (V/SFC) * LD * log(m_total/(m_total - m_fuel))
    # SFC must be in 1/s.
    "SFC_ref": 1.60e-4,        # 1/s, 737-class cruise fuel consumption rate
    "eta_base": 0.15,          # [-], tech sensitivity
    "kv_base": 0.35,           # [-], speed-off-design penalty strength
    "V_ref": 235.0,            # m/s, 737-800-ish cruise speed

    # Aero
    "S_naught": 124.6,         # m^2, 737-800 wing area
    "CD0_base": 0.022,         # [-], clean cruise parasite drag ballpark
    "ks_base": 5.0e-5,         # 1/m^2
    "e_oswald_base": 0.80,     # [-], transport aircraft cruise ballpark

    # Weights
    # These are calibrated model parameters, not literal catalog values.
    # Calibrated so solved m_empty lands near 41,000 kg for a 737-800-class aircraft.
    "m_fuse": 14000.0,         # kg, fixed empty-mass bucket excluding wing/systems/engines
    "kw_base": 95.0,           # calibrated coefficient for wing-mass formula
    "fsys_base": 0.09,         # [-], systems/installed fraction of total mass
    "p_base": 1.0,             # [-]

    # Engine weight
    "m_eng_ref": 5200.0,       # kg, approx two installed CFM56-class engines, rough
    "alpha_base": 0.20,        # [-]

    # Cost model
    "Cf_base": 0.80,           # cost/kg fuel, normalized
    "C_time": 2000.0 / 3600.0, # cost/s, equivalent to 2000 cost/hour
    "k_acq": 0.0001,              # acquisition-cost multiplier
    "C_eng_ref": 2.0e7,        # normalized/reference total engine acquisition cost
    "beta_base": -0.25,         # [-]
}