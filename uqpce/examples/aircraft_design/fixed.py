#python doesnt have POD structs, but you can use 
#the analog of a map in C++ basically

parameters = {

    "R_target" : 5000, #km maybe
    "N_pax" : 300, #num passengers
    "m_payload" : 20000, #kg
    "SFC_ref" : 0.8, #no idea what a realistic num for this is
                     #but this is specific fuel consumpt?
    "S_naught" : 100, #m^2, ref planform area?
    "V_ref" : 200, #m/s, reference free stream speed?
    "m_fuse" : 30000, #kg, fuselage mass
    "CD0_base" : 0.2, #base parasite drag coeff
    "ks_base" : 1.0, #idk what this is 
    "e_oswald_base" : 0.8, #oswald efficiency factor
    "eta_base" : 0.7, #propulsive efficiency?
    "kv_base" : 0.7, #idk what this is either
    "kw_base" : 0.7, #your guess as good as mine
    "fsys_base" : 0.5, #only the lord knows
    "p_base" : 1, #idk bruh
    "alpha_base" : 1, #idt this is AoA
    "beta_base" : 1, #idk 
    "Cf_base" : 0.05, #skin frict coeff
    "m_eng_ref" : 8000, #kg, base engine mass
    "C_time" : 0.8, #idk
    "k_acq" : 1, #idk
    "C_eng_ref" : 1, #idk
}