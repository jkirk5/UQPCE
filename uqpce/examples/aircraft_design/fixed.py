
#737-800 parameters
#sourced from http://www.b737.org.uk/techspecsdetailed.htm
parameters = {
    #~~~~miscelaneous parameters~~~~~~~~~~~~~~~~~~
    "R_target": 4e6,           # try 4000 to 5000 km
    "N_pax": 189,              # num passengers
    "SFC_ref": 1.60e-4,        # 1/s, 737-class cruise fuel consumption rate
    "V_ref": 231.5,            # m/s, 737-800-ish cruise speed
    "S_naught": 124.58,        #[square meters] 737-800 wing area
    "CD0_base": 0.022,         # clean cruise parasite drag ballpark
    "e_oswald_base": 0.80,     # reasonable
    #~~~~miscelaneous parameters~~~~~~~~~~~~~~~~~~
    
    #~~~~~tuning parameters~~~~~~~~~~~~~~~~~~~~~~~~ 
    #determined by inspection using 737-800 values
    "fsys_base": 0.19357,
    "kw_base": 53.0,
    "p_base": 1.0,     #1 until further notice...
    "eta_base": 0.20,       # shitty guesstimate
    "kv_base": 0.20,        # shitty guesstimate
    "alpha_base": -0.20,    # shitty guesstimate
    "beta_base": 0.2,       # shitty guesstimate
    "ks_base": 7.0e-5,    # SHITIEST guesstimate
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #~~revised mass estimates for 737-800 [kg]~~~~~
    "m_fuse": 14518,
    "m_payload_design": 17955.0, 
    "m_payload_max": 20540,
    "m_fuel_max": 21000, #GUESS init-val or COMPARE to out-val
    "m_wing" : 6941, #COMPARE to out-val
    "m_eng_ref" : 8602, #from 2 CFM56-7 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #~~design var initializers based on 737-800~~~~
    "AR" : 9.45,
    "S" : 124.58, #same as 737-800 area
    "V_cruise" : 231.5,
    "SFC_tech" : 0,
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #$$$$$COST STUFF$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    "Cf_base": 0.80,           # cost/kg of fuel
    "C_time": 2000.0 / 3600.0, # cost/s
    "k_acq": 0.0001,  # acquisition-cost multiplier to make approx like cost per flight
    "C_eng_ref": 2.0e7,        # normalized/reference total engine acquisition cost
    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    #extra
    "b" : 34.32 # [meters] 737-800 wing span, use to compare
}


