from fixed import *
import matplotlib.pyplot as plt

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

def plot_uqpce_pretty(prob):

    CL_constraint_dist = prob.get_val('CL_constraint:resampled_responses').ravel()
    print(type(CL_constraint_dist))
    print(np.shape(CL_constraint_dist))
    CL_constraint_ci_lower = prob.get_val('CL_constraint:ci_lower').item()
    CL_constraint_ci_upper = prob.get_val('CL_constraint:ci_upper').item()
    CL_constraint_mu = prob.get_val('CL_constraint:mean').item()
    CL_constraint_var_plus_mu = prob.get_val('CL_constraint:mean_plus_var').item()
    CL_constraint_var = CL_constraint_var_plus_mu - CL_constraint_mu

    DOC_dist = prob.get_val('DOC:resampled_responses').ravel()
    DOC_ci_lower = prob.get_val('DOC:ci_lower').item()
    DOC_ci_upper = prob.get_val('DOC:ci_upper').item()
    DOC_mu = prob.get_val('DOC:mean').item()
    DOC_var_plus_mu = prob.get_val('DOC:mean_plus_var').item()
    DOC_var = DOC_var_plus_mu - DOC_mu

    dpm_dist = prob.get_val('Dpm:resampled_responses').ravel()
    Dpm_ci_lower = prob.get_val('Dpm:ci_lower').item()
    Dpm_ci_upper = prob.get_val('Dpm:ci_upper').item()
    Dpm_mu = prob.get_val('Dpm:mean').item()
    Dpm_var_plus_mu = prob.get_val('Dpm:mean_plus_var').item()
    Dpm_var = Dpm_var_plus_mu - Dpm_mu

    m_fuel_dist = prob.get_val('m_fuel:resampled_responses').ravel()
    m_fuel_ci_lower = prob.get_val('m_fuel:ci_lower').item()
    m_fuel_ci_upper = prob.get_val('m_fuel:ci_upper').item()
    m_fuel_mu = prob.get_val('m_fuel:mean').item()
    m_fuel_var_plus_mu = prob.get_val('m_fuel:mean_plus_var').item()
    m_fuel_var = m_fuel_var_plus_mu - m_fuel_mu

    m_empty_dist = prob.get_val('m_empty:resampled_responses').ravel()
    m_empty_ci_lower = prob.get_val('m_empty:ci_lower').item()
    m_empty_ci_upper = prob.get_val('m_empty:ci_upper').item()
    m_empty_mu = prob.get_val('m_empty:mean').item()
    m_empty_var_plus_mu = prob.get_val('m_empty:mean_plus_var').item()
    m_empty_var = m_empty_var_plus_mu - m_empty_mu

    m_engine_dist = prob.get_val('m_engine:resampled_responses').ravel()
    m_engine_ci_lower = prob.get_val('m_engine:ci_lower').item()
    m_engine_ci_upper = prob.get_val('m_engine:ci_upper').item()
    m_engine_mu = prob.get_val('m_engine:mean').item()
    m_engine_var_plus_mu = prob.get_val('m_engine:mean_plus_var').item()
    m_engine_var = m_engine_var_plus_mu - m_engine_mu

    m_total_dist = prob.get_val('m_total:resampled_responses').ravel()
    m_total_ci_lower = prob.get_val('m_total:ci_lower').item()
    m_total_ci_upper = prob.get_val('m_total:ci_upper').item()
    m_total_mu = prob.get_val('m_total:mean').item()
    m_total_var_plus_mu = prob.get_val('m_total:mean_plus_var').item()
    m_total_var = m_total_var_plus_mu - m_total_mu

    SFC_dist = prob.get_val('SFC:resampled_responses').ravel()
    SFC_ci_lower = prob.get_val('SFC:ci_lower').item()
    SFC_ci_upper = prob.get_val('SFC:ci_upper').item()
    SFC_mu = prob.get_val('SFC:mean').item()
    SFC_var_plus_mu = prob.get_val('SFC:mean_plus_var').item()
    SFC_var = SFC_var_plus_mu - SFC_mu

    CL_dist = prob.get_val('CL:resampled_responses').ravel()
    CL_ci_lower = prob.get_val('CL:ci_lower').item()
    CL_ci_upper = prob.get_val('CL:ci_upper').item()
    CL_mu = prob.get_val('CL:mean').item()
    CL_var_plus_mu = prob.get_val('CL:mean_plus_var').item()
    CL_var = CL_var_plus_mu - CL_mu

    CD_dist = prob.get_val('CD:resampled_responses').ravel()
    CD_ci_lower = prob.get_val('CD:ci_lower').item()
    CD_ci_upper = prob.get_val('CD:ci_upper').item()
    CD_mu = prob.get_val('CD:mean').item()
    CD_var_plus_mu = prob.get_val('CD:mean_plus_var').item()
    CD_var = CD_var_plus_mu - CD_mu


    plt.rcParams.update({
        "text.usetex" : True,
        "font.family" : "serif"
    })

    fig, ax = plt.subplots(2)

    #fig.suptitle(r"Direct Operating Cost PDFs")

    ax[0].hist(DOC_dist,bins=50,density=True)
    ax[0].axvline(DOC_ci_lower, color='red', linewidth=2,linestyle=':', label=rf"CI lower $\approx$ {DOC_ci_lower:.4f}")
    ax[0].axvline(DOC_ci_upper, color='red', linewidth=2,linestyle=':', label=rf"CI upper $\approx$ {DOC_ci_upper:.4f}")
    ax[0].set_xlabel(r"$\mathrm{DOC}$ [USD]",labelpad=15,fontsize=18)
    ax[0].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax[0].set_title(rf"Estimated DOC Distribution: $\mu = {DOC_mu:.4f}, \ \ \sigma^2 = {DOC_var:.4e}$",fontsize=24)
    ax[0].legend()

    ax[1].hist(dpm_dist,bins=50,density=True)
    ax[1].axvline(Dpm_ci_lower, color='red', linewidth=2, linestyle=':', label=rf"CI lower $\approx$ {Dpm_ci_lower:.4e}")
    ax[1].axvline(Dpm_ci_upper, color='red', linewidth=2,linestyle=':',label=rf"CI upper $\approx$ {Dpm_ci_upper:.4e}")
    ax[1].set_xlabel(r"$\mathrm{DOC}_{\mathrm{pkm}} \ \ [\frac{\mathrm{USD}}{\mathrm{px}\cdot\mathrm{km}}]$",labelpad=15,fontsize=18)
    ax[1].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax[1].set_title(rf"Estimated $\mathrm{{DOC}}_{{\mathrm{{pkm}}}}$ Distribution: $\mu = {Dpm_mu:.4e}, \ \ \sigma^2 = {Dpm_var:.4e}$",fontsize=24)
    ax[1].legend(loc="best")

    fig.subplots_adjust(
    hspace=0.5,  # vertical spacing between rows
    wspace=0.3   # horizontal spacing between columns
    )
    
    
    fig_mass, ax_mass = plt.subplots(4)

    ax_mass[2].hist(m_fuel_dist,bins=50,density=True)
    ax_mass[2].axvline(m_fuel_ci_lower, color='red', linewidth=2, linestyle=':', label=rf"CI lower $\approx$ {m_fuel_ci_lower:.4e}")
    ax_mass[2].axvline(m_fuel_ci_upper, color='red', linewidth=2,linestyle=':',label=rf"CI upper $\approx$ {m_fuel_ci_upper:.4e}")
    ax_mass[2].set_xlabel(r"$m_{\mathrm{fuel}}$ [kg]",fontsize=18)
    ax_mass[2].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax_mass[2].set_title(rf"Estimated $m_{{\mathrm{{fuel}}}}$ Distribution $\mu = {m_fuel_mu:.4e}, \ \ \sigma^2 = {m_fuel_var:.4e}$",fontsize=24)
    ax_mass[2].legend()

    ax_mass[1].hist(m_empty_dist,bins=50,density=True)
    ax_mass[1].axvline(m_empty_ci_lower, color='red', linewidth=2, linestyle=':', label=rf"CI lower $\approx$ {m_empty_ci_lower:.4e}")
    ax_mass[1].axvline(m_empty_ci_upper, color='red', linewidth=2,linestyle=':',label=rf"CI upper $\approx$ {m_empty_ci_upper:.4e}")
    ax_mass[1].set_xlabel(r"$m_{\mathrm{empty}}$ [kg]",fontsize=18)
    ax_mass[1].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax_mass[1].set_title(rf"Estimated $m_{{\mathrm{{empty}}}}$ Distribution $\mu = {m_empty_mu:.4e}, \ \ \sigma^2 = {m_empty_var:.4e}$",fontsize=24)
    ax_mass[1].legend()

    ax_mass[0].hist(m_engine_dist,bins=50,density=True)
    ax_mass[0].axvline(m_engine_ci_lower, color='red', linewidth=2, linestyle=':', label=rf"CI lower $\approx$ {m_engine_ci_lower:.4e}")
    ax_mass[0].axvline(m_engine_ci_upper, color='red', linewidth=2,linestyle=':',label=rf"CI upper $\approx$ {m_engine_ci_upper:.4e}")
    ax_mass[0].set_xlabel(r"$m_{\mathrm{engine}}$ [kg]",fontsize=18)
    ax_mass[0].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax_mass[0].set_title(rf"Estimated $m_{{\mathrm{{engine}}}}$ Distribution $\mu = {m_engine_mu:.4e}, \ \ \sigma^2 = {m_engine_var:.4e}$",fontsize=24)
    ax_mass[0].legend()

    ax_mass[3].hist(m_total_dist,bins=50,density=True)
    ax_mass[3].axvline(m_total_ci_lower, color='red', linewidth=2, linestyle=':', label=rf"CI lower $\approx$ {m_total_ci_lower:.4e}")
    ax_mass[3].axvline(m_total_ci_upper, color='red', linewidth=2,linestyle=':',label=rf"CI upper $\approx$ {m_total_ci_upper:.4e}")
    ax_mass[3].set_xlabel(r"$m_{\mathrm{total}}$ [kg]",fontsize=18)
    ax_mass[3].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax_mass[3].set_title(rf"Estimated $m_{{\mathrm{{total}}}}$ Distribution $\mu = {m_total_mu:.4e}, \ \ \sigma^2 = {m_total_var:.4e}$",fontsize=24)
    ax_mass[3].legend()

    fig_cl_constraint, ax_cl_constraint = plt.subplots()

    ax_cl_constraint.hist(CL_constraint_dist,bins=50,density=True)
    ax_cl_constraint.axvline(CL_constraint_ci_lower, color='red', linewidth=2, linestyle=':', label=rf"CI lower $\approx$ {CL_constraint_ci_lower:.4e}")
    ax_cl_constraint.axvline(CL_constraint_ci_upper, color='red', linewidth=2,linestyle=':',label=rf"CI upper $\approx$ {CL_constraint_ci_upper:.4e}")
    ax_cl_constraint.set_xlabel(r"$C_L$ Residual",fontsize=18)
    ax_cl_constraint.set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax_cl_constraint.set_title(rf"Estimated $C_L$ Residual Distribution $C_{{L_{{\mathrm{{target}}}}}}=0.53$, $\mu = {CL_constraint_mu:.4e}, \ \ \sigma^2 = {CL_constraint_var:.4e}$",fontsize=24)
    ax_cl_constraint.legend()

    fig_SFC, ax_SFC = plt.subplots()

    ax_SFC.hist(SFC_dist,bins=50,density=True)
    ax_SFC.axvline(SFC_ci_lower, color='red', linewidth=2, linestyle=':', label=rf"CI lower $\approx$ {SFC_ci_lower:.4e}")
    ax_SFC.axvline(SFC_ci_upper, color='red', linewidth=2,linestyle=':',label=rf"CI upper $\approx$ {SFC_ci_upper:.4e}")
    ax_SFC.set_xlabel(r"$\mathrm{SFC}$",fontsize=18)
    ax_SFC.set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax_SFC.set_title(rf"Estimated $\mathrm{{SFC}}$ Distribution $\mu = {SFC_mu:.4e}, \ \ \sigma^2 = {SFC_var:.4e}$",fontsize=24)
    ax_SFC.legend()

    fig_polar = plt.figure()
    ax_polar = fig_polar.add_subplot(projection='3d')

# Optional: force the histogram to use the physical range you expect
    cd_bins = np.linspace(np.min(CD_dist), np.max(CD_dist), 60)
    cl_bins = np.linspace(np.min(CL_dist), np.max(CL_dist), 60)

    print(cd_bins)

    print(cl_bins)

    hist, cd_edges, cl_edges = np.histogram2d(
        CD_dist,
        CL_dist,
        bins=[cd_bins, cl_bins],
        density=True
    )

    # bar3d wants the lower-left corner of each bar
    cd_left, cl_left = np.meshgrid(
        cd_edges[:-1],
        cl_edges[:-1],
        indexing="ij"
    )

    # Widths of each bin
    dcd, dcl = np.meshgrid(
        np.diff(cd_edges),
        np.diff(cl_edges),
        indexing="ij"
    )

    x = cd_left.ravel()
    y = cl_left.ravel()
    z = np.zeros_like(x)

    dx = dcd.ravel()
    dy = dcl.ravel()
    dz = hist.ravel()

    
    mask = dz > 0
    
    ax_polar.bar3d(
        x[mask],
        y[mask],
        z[mask],
        dx[mask],
        dy[mask],
        dz[mask]
    )

    ax_polar.set_xlabel(r"$C_D$", labelpad=10, fontsize=14)
    ax_polar.set_ylabel(r"$C_L$", labelpad=10, fontsize=14)
    ax_polar.set_zlabel(r"Probability Density", labelpad=10, fontsize=14)

    #ax_polar.set_xlim(0.027, 0.028)
    #ax_polar.set_ylim(0.50, 0.52)

    ax_polar.set_title(r"Joint Distribution of $C_D$ and $C_L$", fontsize=18)
    
    

    plt.show()

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
