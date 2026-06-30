from fixed import *

def display_results(prob):
    print('\n~~~~Outputs~~~~\n\n')
    print('DOC [$/flight]:', prob.get_val('MDA.DOC.DOC'))
    print('\nMASSES\n')
    print('m_total:', prob.get_val('MDA.Mass.m_total'))
    print('m_empty:', prob.get_val('MDA.Weight.m_empty'))
    print('m_fuel:', prob.get_val('MDA.Balance.m_fuel'))
    print('\n~~~~\n')
    print('Range [km]:', prob.get_val('MDA.Range.R')/1000)
    print('\n~~~~\n')
    print('Lift to Drag ratio:', prob.get_val('MDA.Aero.LD'))
    print('Lift Coefficient:', prob.get_val('MDA.Aero.CL'))
    print('Drag Coefficient:',prob.get_val('MDA.Aero.CD'))
    print('\n~~~~\n')
    print('SFC:', prob.get_val('MDA.Prop.SFC'))
    print('Reference SFC:', parameters['SFC_ref'])
    print('\n~~~~Optimized Design~~~~\n\n')
    print('S:', prob.get_val('S'))
    print('AR:', prob.get_val('AR'))
    print('V:', prob.get_val('V'))
    AR_temp = prob.get_val('AR')
    S_temp = prob.get_val('S')
    print('b', np.sqrt(AR_temp*S_temp))
    print('SFC_tech:', prob.get_val('SFC_tech'))

def display_initial_guess(prob):
    print('\n~~~~737-800 Design~~~~\n\n')
    print('S:', prob.get_val('S'))
    print('AR:', prob.get_val('AR'))
    print('V:', prob.get_val('V'))
    print('SFC_tech:', prob.get_val('SFC_tech'))
    print('737-800 DOC estimate [$/flight]:', prob.get_val('MDA.DOC_objective.DOC'))

def initialize(prob):
    prob.set_val('V', optimal['V'])
    prob.set_val('S', optimal['S'])
    prob.set_val('AR', optimal['AR'])
    prob.set_val('SFC_tech', optimal['SFC_tech'])

    # Target range
    prob.set_val('MDA.Balance.R_target', parameters['R_target'])

    # Mass parameters
    prob.set_val('MDA.Balance.m_fuel', 9000.0)
    prob.set_val('MDA.Weight.m_fuse', parameters['m_fuse'])
    prob.set_val('MDA.Engine.m_eng_ref', parameters['m_eng_ref'])
    prob.set_val('MDA.Mass.m_payload', parameters['m_payload_design'])

    # Ref/Environmental parameters
    prob.set_val('MDA.Prop.SFC_ref', parameters['SFC_ref'])
    prob.set_val('MDA.Prop.V_ref', parameters['V_ref'])    
    prob.set_val('MDA.Weight.V_ref', parameters['V_ref'])
    prob.set_val('MDA.Aero.g', 9.80665)
    prob.set_val('MDA.Aero.rho', 0.38)
    prob.set_val('MDA.Aero.C_D0_base', parameters['CD0_base'])
    prob.set_val('MDA.Aero.S_0', parameters['S_naught'])
    prob.set_val('MDA.Aero.e_base', parameters['e_oswald_base'])

    # DOC_objective parameters
    prob.set_val('DOC_objective.Cf_base', parameters['Cf_base'])
    prob.set_val('DOC_objective.C_time', parameters['C_time'])
    prob.set_val('DOC_objective.k_acq', parameters['k_acq'])
    prob.set_val('DOC_objective.C_eng_ref', parameters['C_eng_ref'])
    prob.set_val('DOC_objective.N_pax', parameters['N_pax'])

    #~~~~~tuning parameters
        #fraction of total mass comprising 'systems' and stuff
    prob.set_val('MDA.Weight.fsys_base', parameters['fsys_base'])
        #wing weight regression/fit tuning parameter
    prob.set_val('MDA.Weight.kw_base', parameters['kw_base'])
        #off (faster) design velocity wing weight penalty exponent parameter
    prob.set_val('MDA.Weight.p_base', parameters['p_base'])
        #tuning paramter to change effect SFC_tech has on changing SFC_ref
    prob.set_val('MDA.Prop.eta_base', parameters['eta_base'])
        #off design veloicty penalty to increase SFC qudratically about V_ref
    prob.set_val('MDA.Prop.kv_base', parameters['kv_base'])
        #strength of increase/decrease of amortized engine cost due to SFC_tech
    prob.set_val('DOC_objective.beta_base', parameters['beta_base'])
        #strength of increase/decrease of engine mass due to SFC_tech
    prob.set_val('MDA.Engine.alpha_base', parameters['alpha_base'])
        #pretty hard to estimate this. it represents the sensitivty 
        #of the drag coefficient to changes in planform area linearized 
        #about S_ref. I have no idea what to put for this, but I chose a 
        #small value above. Note units are 1/m**2
    prob.set_val('MDA.Aero.ks_base', parameters['ks_base'])

def initialize_og(prob):
    prob.set_val('V', parameters['V'])
    prob.set_val('S', parameters['S'])
    prob.set_val('AR', parameters['AR'])
    prob.set_val('SFC_tech', parameters['SFC_tech'])

    # Target range
    prob.set_val('aircraft.Balance.R_target', parameters['R_target'])

    # Mass parameters
    prob.set_val('aircraft.Balance.m_fuel', 9000.0)
    prob.set_val('aircraft.Weight.m_fuse', parameters['m_fuse'])
    prob.set_val('aircraft.Engine.m_eng_ref', parameters['m_eng_ref'])
    prob.set_val('aircraft.Mass.m_payload', parameters['m_payload_design'])

    # Ref/Environmental parameters
    prob.set_val('aircraft.Prop.SFC_ref', parameters['SFC_ref'])
    prob.set_val('aircraft.Prop.V_ref', parameters['V_ref'])    
    prob.set_val('aircraft.Weight.V_ref', parameters['V_ref'])
    prob.set_val('aircraft.Aero.g', 9.80665)
    prob.set_val('aircraft.Aero.rho', 0.38)
    prob.set_val('aircraft.Aero.C_D0_base', parameters['CD0_base'])
    prob.set_val('aircraft.Aero.S_0', parameters['S_naught'])
    prob.set_val('aircraft.Aero.e_base', parameters['e_oswald_base'])

    # DOC parameters
    prob.set_val('aircraft.DOC.Cf_base', parameters['Cf_base'])
    prob.set_val('aircraft.DOC.C_time', parameters['C_time'])
    prob.set_val('aircraft.DOC.k_acq', parameters['k_acq'])
    prob.set_val('aircraft.DOC.C_eng_ref', parameters['C_eng_ref'])
    prob.set_val('aircraft.DOC.N_pax', parameters['N_pax'])

    #~~~~~tuning parameters
        #fraction of total mass comprising 'systems' and stuff
    prob.set_val('aircraft.Weight.fsys_base', parameters['fsys_base'])
        #wing weight regression/fit tuning parameter
    prob.set_val('aircraft.Weight.kw_base', parameters['kw_base'])
        #off (faster) design velocity wing weight penalty exponent parameter
    prob.set_val('aircraft.Weight.p_base', parameters['p_base'])
        #tuning paramter to change effect SFC_tech has on changing SFC_ref
    prob.set_val('aircraft.Prop.eta_base', parameters['eta_base'])
        #off design veloicty penalty to increase SFC qudratically about V_ref
    prob.set_val('aircraft.Prop.kv_base', parameters['kv_base'])
        #strength of increase/decrease of amortized engine cost due to SFC_tech
    prob.set_val('aircraft.DOC.beta_base', parameters['beta_base'])
        #strength of increase/decrease of engine mass due to SFC_tech
    prob.set_val('aircraft.Engine.alpha_base', parameters['alpha_base'])
        #pretty hard to estimate this. it represents the sensitivty 
        #of the drag coefficient to changes in planform area linearized 
        #about S_ref. I have no idea what to put for this, but I chose a 
        #small value above. Note units are 1/m**2
    prob.set_val('aircraft.Aero.ks_base', parameters['ks_base'])


import numpy as np
from scipy.special import erfinv, erf
#function the returns a distribution of input variables on CI
def distribute_input(CI,base_val,sigma,n_points):
    mu = 1
    p_lower = (1-CI)/2 #lower end sample point
    p_upper = (1 + CI)/2

    p = np.linspace(p_lower,p_upper,n_points)

    delta_vec = erfinv(2*p - 1)*np.sqrt(2)*sigma + mu

    CDF_vec = (1.0/2.0)*erf((delta_vec-mu)/(np.sqrt(2)*sigma)) + 0.5

    u_vec = (delta_vec-mu)/(np.sqrt(2)*sigma)

    PDF_vec = (1.0/(sigma*np.sqrt(2*np.pi)))*np.exp(-(u_vec**2))

    #print(delta_vec)

    return delta_vec*base_val, CDF_vec, PDF_vec
