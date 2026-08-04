# Sourced from http://www.b737.org.uk/techspecsdetailed.htm
parameters = {
    "R_target": 5.5e6,              # m
    "N_pax": 189.0,                 # -
    "SFC_ref": 1.6e-4,              # 1/s
    "V_ref": 231.5,                 # m/s
    "S_naught": 124.58,             # m**2
    "CD0_base": 0.022,              # -
    "e_oswald_base": 0.80,          # -
    "m_fuse": 14518.0,              # kg
    "m_payload_design": 17955.0,    # kg
    "m_payload_max": 20540.0,       # kg
    "m_fuel_max": 21000.0,          # kg
    "m_wing": 6941.0,               # kg
    "m_eng_ref": 8602.0,            # kg
    "m_total": 50000.0,             # kg

    "wing_load": 5905.0,            # N/m**2
    "AR": 9.45,                     # -
    "S": 124.58,                    # m**2
    "V_cruise": 240.5,              # m/s
    "SFC_tech": 0.0,                # -

    "Cf_base": 0.74,                # USD/kg
    "C_time": 0.472,                # USD/s; =1700 USD/hr
    "k_acq": 0.00142,               # -
    "C_eng_ref": 2.2e7,             # USD

    "b": 34.32,                     # m
    "g": 9.81,                      # m/s**2
    "rho": 0.38,                    # kg/m**3
}

tuning = {  
    "p_base": 7.5443750000000005,       # -
    "eta_base": 0.4393500000352975,     # -
    "kv_base": 601.05144999999999,      # -
    "alpha_base": 0.345000107456725,    # -
    "beta_base": 0.55,                  # -
    "ks_base": 0.0002910700075464138,   # 1/m**2
    "fsys_base": 0.19357,               # -
    "kw_base": 53.0,                    # -?
}