#737-800 Parameters
#Sourced from http://www.b737.org.uk/techspecsdetailed.htm

parameters = {
    #~~~~miscelaneous parameters~~~~~~~~~~~~~~~~~~
    "R_target": 4.6e6,          # [m], target range; 4000-5000 km
    "N_pax": 189,               # Number of passengers
    "SFC_ref": 1.60e-4,         # [1/s], 737-class cruise fuel consumption rate
    "V_ref": 231.5,             # [m/s], 737-800-ish cruise speed
    "S_naught": 124.58,         # [m^2], 737-800 wing area
    "CD0_base": 0.022,          # Clean cruise parasite drag ballpark
    "e_oswald_base": 0.80,      # Oswald efficiency
    #~~~~miscelaneous parameters~~~~~~~~~~~~~~~~~~
   
    #~~~~~tuning parameters~~~~~~~~~~~~~~~~~~~~~~~~
    #Determined by inspection using 737-800 values
    "fsys_base": 0.19357,       # Systems fraction
    "kw_base": 53.0,            # Wing mass
    "p_base": 5.3,              # Speed-weight
    "eta_base": 0.40,           # SFC benefit rate
    "kv_base": 11.5,            # Speed penalty
    "alpha_base": 0.10,         # Engine mass scaling
    "beta_base": 0.2,           # Engine cost scaling
    "ks_base": 2.0e-5,          # Drag-size scaling
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
    #~~revised mass estimates for 737-800 [kg]~~~~~
    "m_fuse": 14518,                # Fuselage mass
    "m_payload_design": 17955.0,    # Payload design mass
    "m_payload_max": 20540,         # Max payload mass
    "m_fuel_max": 21000,            # Max fuel mass
    "m_wing" : 6941,                # Wing mass
    "m_eng_ref" : 8602,             # Reference engine mass; from 2 CFM56-7
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
    #~~design var initializers based on 737-800~~~~
    "AR" : 9.45,                # Aspect ratio
    "S" : 124.58,               # [m^2], wing area; same as 737-800 area
    "V" : 231.,                # [m/s], cruise speed
    "SFC_tech" : 0,             # SFC technology factor (-1 to 1)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
    #$$$$$COST STUFF$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    "Cf_base": 0.80,            # [USD/kg], cost/kg of fuel
    "C_time": 2000.0,           # [USD/hr] cost/time
    "k_acq": 0.00122,           # Highly senssitive but interval seems to shift up with range
    "C_eng_ref": 2.0e7,         # [USD], normalized/reference total engine acquisition cost
    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 
    #extra
    "b" : 34.32                 # [m] 737-800 wing span, use to compare
}