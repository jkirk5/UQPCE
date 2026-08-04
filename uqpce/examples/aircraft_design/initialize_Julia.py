from fixed import parameters, tuning

def initialize(prob, design_params):
    prob.set_val('V_cruise', design_params['V_cruise'], units='m/s')
    prob.set_val('S', design_params['S'], units='m**2')
    prob.set_val('AR', design_params['AR'])
    prob.set_val('SFC_tech', design_params['SFC_tech'])

    # Target range
    prob.set_val('R_target', parameters['R_target'], units='m')

    # Mass parameters
    prob.set_val('m_fuel', 9000.0, units='kg')
    prob.set_val('m_fuse', parameters['m_fuse'], units='kg')
    prob.set_val('m_eng_ref', parameters['m_eng_ref'], units='kg')
    prob.set_val('m_payload', parameters['m_payload_design'], units='kg')

    # Ref/Environmental parameters
    prob.set_val('SFC_ref', parameters['SFC_ref'], units='1/s')
    prob.set_val('V_ref', parameters['V_ref'], units='m/s')    
    prob.set_val('g', parameters['g'], units='m/s**2')
    prob.set_val('rho', parameters['rho'], units='kg/m**3')
    prob.set_val('C_D0_base', parameters['CD0_base'])
    prob.set_val('S_0', parameters['S_naught'], units='m**2')
    prob.set_val('e_base', parameters['e_oswald_base'])

    # DOC parameters
    prob.set_val('Cf_base', parameters['Cf_base'], units='USD/kg')
    prob.set_val('C_time', parameters['C_time'], units='USD/s')
    prob.set_val('k_acq', parameters['k_acq'])
    prob.set_val('C_eng_ref', parameters['C_eng_ref'], units='USD')
    prob.set_val('N_pax', parameters['N_pax'])

    #~~~~~tuning parameters
    prob.set_val('fsys_base', tuning['fsys_base'])      #fraction of total mass comprising 'systems' and stuff
    prob.set_val('kw_base', tuning['kw_base'])          #wing weight regression/fit tuning parameter
    prob.set_val('p_base', tuning['p_base'])            #off (faster) design velocity wing weight penalty exponent parameter
    prob.set_val('eta_base', tuning['eta_base'])        #tuning paramter to change effect SFC_tech has on changing SFC_ref
    prob.set_val('kv_base', tuning['kv_base'])          #off design velocity penalty to increase SFC quadratically about V_ref
    prob.set_val('beta_base', tuning['beta_base'])      #strength of increase/decrease of amortized engine cost due to SFC_tech
    prob.set_val('alpha_base', tuning['alpha_base'])    #strength of increase/decrease of engine mass due to SFC_tech
    prob.set_val('ks_base', tuning['ks_base'], units='1/m**2')
        #pretty hard to estimate this. it represents the sensitivty 
        #of the drag coefficient to changes in planform area linearized 
        #about S_ref. I have no idea what to put for this, but I chose a 
        #small value above. Note units are 1/m**2