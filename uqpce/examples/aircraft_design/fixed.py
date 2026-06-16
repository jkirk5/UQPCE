
#737-800 parameters
#sourced from http://www.b737.org.uk/techspecsdetailed.htm
parameters = {
    #
    "R_target": 4.5e6,           # m
    "N_pax": 180,                # num passengers
    "m_payload_design": 17955.0, #kg
    "m_payload_max": 20540,      #kg
    

    "SFC_ref": 1.60e-4,        # 1/s, 737-class cruise fuel consumption rate
    "eta_base": 0.15,          # [-], tech sensitivity
    "kv_base": 0.35,           # [-], speed-off-design penalty strength
    "V_ref": 235.0,            # m/s, 737-800-ish cruise speed

    # Aero
    "S_naught": 124.58,        # m^2, 737-800 wing area
    "b" : 34.32,               #meters, span is not design varibale, but useful regardless
    "CD0_base": 0.022,         # clean cruise parasite drag ballpark
    "ks_base": 5.0e-5,         # 1/m^2
    "e_oswald_base": 0.80,     # transport aircraft cruise ballpark

    # Weights
    "m_fuse": 14000.0,         # kg, fixed empty-mass bucket excluding wing/systems/engines
    "kw_base": 95.0,           # calibrated coefficient for wing-mass formula
    "fsys_base": 0.09,         # systems/installed fraction of total mass
    "p_base": 1.0,             # not sure

    # Engine weight
    "m_eng_ref": 5200.0,       # kg, approx two installed CFM56-class engines, rough
    "alpha_base": 0.20,        # not sure

    # Cost model
    "Cf_base": 0.80,           # cost/kg fuel, normalized
    "C_time": 2000.0 / 3600.0, # cost/s, equivalent to 2000 cost/hour
    "k_acq": 0.0001,           # acquisition-cost multiplier to make approx like cost per flight
    "C_eng_ref": 2.0e7,        # normalized/reference total engine acquisition cost
    "beta_base": -0.25,        # not sure
}