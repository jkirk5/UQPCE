from fixed import parameters, tuning
import matplotlib.pyplot as plt
import numpy as np

def display_results(prob):
    print('\n~~~~Outputs~~~~\n\n')
    print('DOC [$/flight]:', prob.get_val('DOC'))
    print('\nMASSES\n')
    print('m_total:', prob.get_val('m_total'))
    print('m_empty:', prob.get_val('m_empty'))
    print('m_fuel:', prob.get_val('m_fuel'))
    print('\n~~~~\n')
    print('Range [km]:', prob.get_val('R')/1000)
    print('\n~~~~\n')
    print('Lift to Drag ratio:', prob.get_val('LD'))
    print('Lift Coefficient:', prob.get_val('CL'))
    print('Wing Loading [N/m^2]:', prob.get_val('WL'))
    print('Wing Loading Constr [N/m^2]:', prob.get_val('WL_constraint'))
    print('Drag Coefficient:',prob.get_val('CD'))
    print('\n~~~~\n')
    print('SFC:', prob.get_val('SFC'))
    print('Reference SFC:', parameters['SFC_ref'])
    print('\n~~~~Optimized Design~~~~\n\n')
    print('S:', prob.get_val('S'))
    print('AR:', prob.get_val('AR'))
    print('V_cruise:', prob.get_val('V_cruise'))
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

def initialize(prob, design_params=parameters):
    prob.set_val('V_cruise', design_params['V_cruise'])
    prob.set_val('S', design_params['S'])
    prob.set_val('AR', design_params['AR'])
    prob.set_val('SFC_tech', design_params['SFC_tech'])

    #~~~~~tuning parameters
    prob.set_val('e_base', parameters['e_oswald_base'])
    prob.set_val('C_D0_base', parameters['CD0_base'])
    prob.set_val('Cf_base', parameters['Cf_base'])
    prob.set_val('fsys_base', tuning['fsys_base'])          # fraction of total mass comprising 'systems' and stuff
    prob.set_val('kw_base', tuning['kw_base'])              # wing weight regression/fit tuning parameter
    prob.set_val('p_base', tuning['p_base'])                # off (faster) design velocity wing weight penalty exponent parameter
    prob.set_val('eta_base', tuning['eta_base'])            # tuning paramter to change effect SFC_tech has on changing SFC_ref
    prob.set_val('kv_base', tuning['kv_base'])              # off design veloicty penalty to increase SFC qudratically about V_ref
    prob.set_val('beta_base', tuning['beta_base'])          # strength of increase/decrease of amortized engine cost due to SFC_tech
    prob.set_val('alpha_base', tuning['alpha_base'])        # strength of increase/decrease of engine mass due to SFC_tech
    prob.set_val('ks_base', tuning['ks_base'])              # pretty hard to estimate this. it represents the sensitivty 
                                                            # of the drag coefficient to changes in planform area linearized 
                                                            # about S_ref. I have no idea what to put for this, but I chose a 
                                                            # small value above. Note units are 1/m**2

def plot_uqpce_pretty(prob):

    CL_constraint_dist = prob.get_val('CL:resampled_responses').ravel()
    print(type(CL_constraint_dist))
    print(np.shape(CL_constraint_dist))
    CL_constraint_ci_lower = prob.get_val('CL:ci_lower').item()
    CL_constraint_ci_upper = prob.get_val('CL:ci_upper').item()
    CL_constraint_mu = prob.get_val('CL:mean').item()
    CL_constraint_var_plus_mu = prob.get_val('CL:mean_plus_var').item()
    CL_constraint_var = CL_constraint_var_plus_mu - CL_constraint_mu

    DOC_dist = prob.get_val('DOC:resampled_responses').ravel()
    DOC_ci_lower = prob.get_val('DOC:ci_lower').item()
    DOC_ci_upper = prob.get_val('DOC:ci_upper').item()
    DOC_mu = prob.get_val('DOC:mean').item()
    DOC_var_plus_mu = prob.get_val('DOC:mean_plus_var').item()
    DOC_var = DOC_var_plus_mu - DOC_mu

    """
       dpm_dist = prob.get_val('Dpm:resampled_responses').ravel()
    Dpm_ci_lower = prob.get_val('Dpm:ci_lower').item()
    Dpm_ci_upper = prob.get_val('Dpm:ci_upper').item()
    Dpm_mu = prob.get_val('Dpm:mean').item()
    Dpm_var_plus_mu = prob.get_val('Dpm:mean_plus_var').item()
    Dpm_var = Dpm_var_plus_mu - Dpm_mu
    """
 

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

    fig, ax = plt.subplots()

    #fig.suptitle(r"Direct Operating Cost PDFs")

    ax.hist(DOC_dist,bins=50,density=True)
    ax.axvline(DOC_ci_lower, color='red', linewidth=2,linestyle=':', label=rf"CI lower $\approx$ {DOC_ci_lower:.4f}")
    ax.axvline(DOC_ci_upper, color='red', linewidth=2,linestyle=':', label=rf"CI upper $\approx$ {DOC_ci_upper:.4f}")
    ax.set_xlabel(r"$\mathrm{DOC}$ [USD]",labelpad=15,fontsize=18)
    ax.set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax.set_title(rf"Estimated DOC Distribution: $\mu = {DOC_mu:.4f}, \ \ \sigma^2 = {DOC_var:.4e}$",fontsize=24)
    ax.legend()

    

    fig.subplots_adjust(
    hspace=0.5,  # vertical spacing between rows
    wspace=0.3   # horizontal spacing between columns
    )
    
    """
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
    """

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

def plot_objective(dict_response, dict_optimized):

    DOC_dist = dict_response["DOC"]["dist"]
    DOC_ci_lower = dict_response["DOC"]["ci_lower"]
    DOC_ci_upper = dict_response["DOC"]["ci_upper"]
    DOC_mu = dict_response["DOC"]["mu"]
    DOC_var_plus_mu = dict_response["DOC"]["var_plus_mu"]
    DOC_var = dict_response["DOC"]["var"]

    DOC_opt_dist = dict_optimized["DOC"]["dist"]
    DOC_opt_ci_lower = dict_optimized["DOC"]["ci_lower"]
    DOC_opt_ci_upper = dict_optimized["DOC"]["ci_upper"]
    DOC_opt_mu =  dict_optimized["DOC"]["mu"]
    DOC_opt_var_plus_mu = dict_optimized["DOC"]["var_plus_mu"]
    DOC_opt_var = dict_optimized["DOC"]["var"]
    
    Dpm_dist = dict_response["Dpm"]["dist"]
    Dpm_ci_lower = dict_response["Dpm"]["ci_lower"]
    Dpm_ci_upper = dict_response["Dpm"]["ci_upper"]
    Dpm_mu = dict_response["Dpm"]["mu"]
    Dpm_var_plus_mu = dict_response["Dpm"]["var_plus_mu"]
    Dpm_var = dict_response["Dpm"]["var"]

    Dpm_opt_dist = dict_optimized["Dpm"]["dist"]
    Dpm_opt_ci_lower = dict_optimized["Dpm"]["ci_lower"]
    Dpm_opt_ci_upper = dict_optimized["Dpm"]["ci_upper"]
    Dpm_opt_mu = dict_optimized["Dpm"]["mu"]
    Dpm_opt_var_plus_mu = dict_optimized["Dpm"]["var_plus_mu"]
    Dpm_opt_var = dict_optimized["Dpm"]["var"]

    fig, ax = plt.subplots(2, 1, figsize=(14, 14))

    fig.suptitle(
        r"Objective Probability Distributions",
        fontsize=28
    )
  
    ax[0].hist(DOC_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")
    
    ax[0].axvline(DOC_ci_lower, color='red', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {DOC_ci_lower:.4f}")
    ax[0].axvline(DOC_ci_upper, color='red', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {DOC_ci_upper:.4f}")
    ax[0].axvline(DOC_mu, color='red', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {DOC_mu:.4f}")
 
    ax[0].hist(DOC_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")
    
    ax[0].axvline(DOC_opt_ci_lower, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {DOC_opt_ci_lower:.4f}")
    ax[0].axvline(DOC_opt_ci_upper, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {DOC_opt_ci_upper:.4f}")
    ax[0].axvline(DOC_opt_mu, color='blue', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {DOC_opt_mu:.4f}")
    
    ax[0].set_xlabel(r"$\mathrm{DOC}$ [$\mathrm{USD}$]",labelpad=15,fontsize=18)
    ax[0].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax[0].set_title(rf"DOC Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {DOC_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {DOC_opt_var:.4e}$",fontsize=24)
    ax[0].legend()

    ax[1].hist(Dpm_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")
    
    ax[1].axvline(Dpm_ci_lower, color='red', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {Dpm_ci_lower:.4f}")
    ax[1].axvline(Dpm_ci_upper, color='red', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {Dpm_ci_upper:.4f}")
    ax[1].axvline(Dpm_mu, color='red', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {Dpm_mu:.4f}")
 
    ax[1].hist(Dpm_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")
    
    ax[1].axvline(Dpm_opt_ci_lower, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {Dpm_opt_ci_lower:.4f}")
    ax[1].axvline(Dpm_opt_ci_upper, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {Dpm_opt_ci_upper:.4f}")
    ax[1].axvline(Dpm_opt_mu, color='blue', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {Dpm_opt_mu:.4f}")
    
    ax[1].set_xlabel(r"$\mathrm{Dpm}$ [$\frac{\mathrm{USD}}{\mathrm{px} \cdot km}$]",labelpad=15,fontsize=18)
    ax[1].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax[1].set_title(rf"DOC Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {Dpm_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {Dpm_opt_var:.4e}$",fontsize=24)
    ax[1].legend()


    plt.show()

def plot_coefficients(dict_response, dict_optimized):

    CL_dist = dict_response["CL"]["dist"]
    CL_ci_lower = dict_response["CL"]["ci_lower"]
    CL_ci_upper = dict_response["CL"]["ci_upper"]
    CL_mu = dict_response["CL"]["mu"]
    CL_var_plus_mu = dict_response["CL"]["var_plus_mu"]
    CL_var = dict_response["CL"]["var"]

    CL_opt_dist = dict_optimized["CL"]["dist"]
    CL_opt_ci_lower = dict_optimized["CL"]["ci_lower"]
    CL_opt_ci_upper = dict_optimized["CL"]["ci_upper"]
    CL_opt_mu = dict_optimized["CL"]["mu"]
    CL_opt_var_plus_mu = dict_optimized["CL"]["var_plus_mu"]
    CL_opt_var = dict_optimized["CL"]["var"]
    
    CD_dist = dict_response["CD"]["dist"]
    CD_ci_lower = dict_response["CD"]["ci_lower"]
    CD_ci_upper = dict_response["CD"]["ci_upper"]
    CD_mu = dict_response["CD"]["mu"]
    CD_var_plus_mu = dict_response["CD"]["var_plus_mu"]
    CD_var = dict_response["CD"]["var"]

    CD_opt_dist = dict_optimized["CD"]["dist"]
    CD_opt_ci_lower = dict_optimized["CD"]["ci_lower"]
    CD_opt_ci_upper = dict_optimized["CD"]["ci_upper"]
    CD_opt_mu = dict_optimized["CD"]["mu"]
    CD_opt_var_plus_mu = dict_optimized["CD"]["var_plus_mu"]
    CD_opt_var = dict_optimized["CD"]["var"]

    fig, ax = plt.subplots(2, 1, figsize=(14, 14))

    fig.suptitle(
        r"Aerodynamic Coefficient Probability Distributions",
        fontsize=28
    )
  
    ax[0].hist(CL_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")
    
    ax[0].axvline(CL_ci_lower, color='red', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {CL_ci_lower:.4f}")
    ax[0].axvline(CL_ci_upper, color='red', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {CL_ci_upper:.4f}")
    ax[0].axvline(CL_mu, color='red', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {CL_mu:.4f}")
 
    ax[0].hist(CL_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")
    
    ax[0].axvline(CL_opt_ci_lower, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {CL_opt_ci_lower:.4f}")
    ax[0].axvline(CL_opt_ci_upper, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {CL_opt_ci_upper:.4f}")
    ax[0].axvline(CL_opt_mu, color='blue', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {CL_opt_mu:.4f}")
    
    ax[0].set_xlabel(r"$C_L$",labelpad=15,fontsize=18)
    ax[0].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax[0].set_title(rf"$C_L$ Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {CL_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {CL_opt_var:.4e}$",fontsize=24)
    ax[0].legend()

    ax[1].hist(CD_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")
    
    ax[1].axvline(CD_ci_lower, color='red', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {CD_ci_lower:.4f}")
    ax[1].axvline(CD_ci_upper, color='red', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {CD_ci_upper:.4f}")
    ax[1].axvline(CD_mu, color='red', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {CD_mu:.4f}")
 
    ax[1].hist(CD_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")
    
    ax[1].axvline(CD_opt_ci_lower, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {CD_opt_ci_lower:.4f}")
    ax[1].axvline(CD_opt_ci_upper, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {CD_opt_ci_upper:.4f}")
    ax[1].axvline(CD_opt_mu, color='blue', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {CD_opt_mu:.4f}")
    
    ax[1].set_xlabel(r"$C_D$",labelpad=15,fontsize=18)
    ax[1].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax[1].set_title(rf"$C_D$ Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {CD_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {CD_opt_var:.4e}$",fontsize=24)
    ax[1].legend()

    plt.show()

def plot_constraints(dict_response, dict_optimized):

    CL_constraint_dist = dict_response["CL_constraint"]["dist"]
    CL_constraint_ci_lower = dict_response["CL_constraint"]["ci_lower"]
    CL_constraint_ci_upper = dict_response["CL_constraint"]["ci_upper"]
    CL_constraint_mu = dict_response["CL_constraint"]["mu"]
    CL_constraint_var_plus_mu = dict_response["CL_constraint"]["var_plus_mu"]
    CL_constraint_var = dict_response["CL_constraint"]["var"]

    CL_constraint_opt_dist = dict_optimized["CL_constraint"]["dist"]
    CL_constraint_opt_ci_lower = dict_optimized["CL_constraint"]["ci_lower"]
    CL_constraint_opt_ci_upper = dict_optimized["CL_constraint"]["ci_upper"]
    CL_constraint_opt_mu = dict_optimized["CL_constraint"]["mu"]
    CL_constraint_opt_var_plus_mu = dict_optimized["CL_constraint"]["var_plus_mu"]
    CL_constraint_opt_var = dict_optimized["CL_constraint"]["var"]
    
    WL_constraint_dist = dict_response["WL_constraint"]["dist"]
    WL_constraint_ci_lower = dict_response["WL_constraint"]["ci_lower"]
    WL_constraint_ci_upper = dict_response["WL_constraint"]["ci_upper"]
    WL_constraint_mu = dict_response["WL_constraint"]["mu"]
    WL_constraint_var_plus_mu = dict_response["WL_constraint"]["var_plus_mu"]
    WL_constraint_var = dict_response["WL_constraint"]["var"]

    WL_constraint_opt_dist = dict_optimized["WL_constraint"]["dist"]
    WL_constraint_opt_ci_lower = dict_optimized["WL_constraint"]["ci_lower"]
    WL_constraint_opt_ci_upper = dict_optimized["WL_constraint"]["ci_upper"]
    WL_constraint_opt_mu = dict_optimized["WL_constraint"]["mu"]
    WL_constraint_opt_var_plus_mu = dict_optimized["WL_constraint"]["var_plus_mu"]
    WL_constraint_opt_var = dict_optimized["WL_constraint"]["var"]

    fig, ax = plt.subplots(2, 1, figsize=(14, 14))

    fig.suptitle(
        r"Constraint Probability Distributions",
        fontsize=28
    )
  
    ax[0].hist(CL_constraint_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")
    
    ax[0].axvline(CL_constraint_ci_lower, color='red', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {CL_constraint_ci_lower:.4f}")
    ax[0].axvline(CL_constraint_ci_upper, color='red', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {CL_constraint_ci_upper:.4f}")
    ax[0].axvline(CL_constraint_mu, color='red', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {CL_constraint_mu:.4f}")
 
    ax[0].hist(CL_constraint_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")
    
    ax[0].axvline(CL_constraint_opt_ci_lower, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {CL_constraint_opt_ci_lower:.4f}")
    ax[0].axvline(CL_constraint_opt_ci_upper, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {CL_constraint_opt_ci_upper:.4f}")
    ax[0].axvline(CL_constraint_opt_mu, color='blue', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {CL_constraint_opt_mu:.4f}")
    
    ax[0].set_xlabel(r"$\mathrm{CL\ Constraint}$ [-]",labelpad=15,fontsize=18)
    ax[0].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax[0].set_title(rf"CL Constraint Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {CL_constraint_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {CL_constraint_opt_var:.4e}$",fontsize=24)
    ax[0].legend()

    ax[1].hist(WL_constraint_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")
    
    ax[1].axvline(WL_constraint_ci_lower, color='red', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {WL_constraint_ci_lower:.4f}")
    ax[1].axvline(WL_constraint_ci_upper, color='red', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {WL_constraint_ci_upper:.4f}")
    ax[1].axvline(WL_constraint_mu, color='red', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {WL_constraint_mu:.4f}")
 
    ax[1].hist(WL_constraint_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")
    
    ax[1].axvline(WL_constraint_opt_ci_lower, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {WL_constraint_opt_ci_lower:.4f}")
    ax[1].axvline(WL_constraint_opt_ci_upper, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {WL_constraint_opt_ci_upper:.4f}")
    ax[1].axvline(WL_constraint_opt_mu, color='blue', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {WL_constraint_opt_mu:.4f}")
    
    ax[1].set_xlabel(r"$\mathrm{WL\ Constraint}$ [-]",labelpad=15,fontsize=18)
    ax[1].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax[1].set_title(rf"WL Constraint Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {WL_constraint_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {WL_constraint_opt_var:.4e}$",fontsize=24)
    ax[1].legend()

    plt.show()

def plot_mass(dict_response, dict_optimized):

    m_total_dist = dict_response["m_total"]["dist"]
    m_total_ci_lower = dict_response["m_total"]["ci_lower"]
    m_total_ci_upper = dict_response["m_total"]["ci_upper"]
    m_total_mu = dict_response["m_total"]["mu"]
    m_total_var_plus_mu = dict_response["m_total"]["var_plus_mu"]
    m_total_var = dict_response["m_total"]["var"]

    m_total_opt_dist = dict_optimized["m_total"]["dist"]
    m_total_opt_ci_lower = dict_optimized["m_total"]["ci_lower"]
    m_total_opt_ci_upper = dict_optimized["m_total"]["ci_upper"]
    m_total_opt_mu = dict_optimized["m_total"]["mu"]
    m_total_opt_var_plus_mu = dict_optimized["m_total"]["var_plus_mu"]
    m_total_opt_var = dict_optimized["m_total"]["var"]

    m_fuel_dist = dict_response["m_fuel"]["dist"]
    m_fuel_ci_lower = dict_response["m_fuel"]["ci_lower"]
    m_fuel_ci_upper = dict_response["m_fuel"]["ci_upper"]
    m_fuel_mu = dict_response["m_fuel"]["mu"]
    m_fuel_var_plus_mu = dict_response["m_fuel"]["var_plus_mu"]
    m_fuel_var = dict_response["m_fuel"]["var"]

    m_fuel_opt_dist = dict_optimized["m_fuel"]["dist"]
    m_fuel_opt_ci_lower = dict_optimized["m_fuel"]["ci_lower"]
    m_fuel_opt_ci_upper = dict_optimized["m_fuel"]["ci_upper"]
    m_fuel_opt_mu = dict_optimized["m_fuel"]["mu"]
    m_fuel_opt_var_plus_mu = dict_optimized["m_fuel"]["var_plus_mu"]
    m_fuel_opt_var = dict_optimized["m_fuel"]["var"]

    m_empty_dist = dict_response["m_empty"]["dist"]
    m_empty_ci_lower = dict_response["m_empty"]["ci_lower"]
    m_empty_ci_upper = dict_response["m_empty"]["ci_upper"]
    m_empty_mu = dict_response["m_empty"]["mu"]
    m_empty_var_plus_mu = dict_response["m_empty"]["var_plus_mu"]
    m_empty_var = dict_response["m_empty"]["var"]

    m_empty_opt_dist = dict_optimized["m_empty"]["dist"]
    m_empty_opt_ci_lower = dict_optimized["m_empty"]["ci_lower"]
    m_empty_opt_ci_upper = dict_optimized["m_empty"]["ci_upper"]
    m_empty_opt_mu = dict_optimized["m_empty"]["mu"]
    m_empty_opt_var_plus_mu = dict_optimized["m_empty"]["var_plus_mu"]
    m_empty_opt_var = dict_optimized["m_empty"]["var"]

    m_engine_dist = dict_response["m_engine"]["dist"]
    m_engine_ci_lower = dict_response["m_engine"]["ci_lower"]
    m_engine_ci_upper = dict_response["m_engine"]["ci_upper"]
    m_engine_mu = dict_response["m_engine"]["mu"]
    m_engine_var_plus_mu = dict_response["m_engine"]["var_plus_mu"]
    m_engine_var = dict_response["m_engine"]["var"]

    m_engine_opt_dist = dict_optimized["m_engine"]["dist"]
    m_engine_opt_ci_lower = dict_optimized["m_engine"]["ci_lower"]
    m_engine_opt_ci_upper = dict_optimized["m_engine"]["ci_upper"]
    m_engine_opt_mu = dict_optimized["m_engine"]["mu"]
    m_engine_opt_var_plus_mu = dict_optimized["m_engine"]["var_plus_mu"]
    m_engine_opt_var = dict_optimized["m_engine"]["var"]

    fig_total_fuel, ax_total_fuel = plt.subplots(2, 1, figsize=(14, 14))

    fig_total_fuel.suptitle(
        r"Total and Fuel Mass Probability Distributions",
        fontsize=28
    )

    ax_total_fuel[0].hist(m_total_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")

    ax_total_fuel[0].axvline(m_total_ci_lower, color='red', linewidth=2,linestyle=':',
               label=rf"CI lower $\approx$ {m_total_ci_lower:.4f}")
    ax_total_fuel[0].axvline(m_total_ci_upper, color='red', linewidth=2,linestyle=':',
               label=rf"CI upper $\approx$ {m_total_ci_upper:.4f}")
    ax_total_fuel[0].axvline(m_total_mu, color='red', linewidth=2,linestyle='-',
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {m_total_mu:.4f}")

    ax_total_fuel[0].hist(m_total_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")

    ax_total_fuel[0].axvline(m_total_opt_ci_lower, color='blue', linewidth=2,linestyle=':',
               label=rf"CI lower $\approx$ {m_total_opt_ci_lower:.4f}")
    ax_total_fuel[0].axvline(m_total_opt_ci_upper, color='blue', linewidth=2,linestyle=':',
               label=rf"CI upper $\approx$ {m_total_opt_ci_upper:.4f}")
    ax_total_fuel[0].axvline(m_total_opt_mu, color='blue', linewidth=2,linestyle='-',
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {m_total_opt_mu:.4f}")

    ax_total_fuel[0].set_xlabel(r"$m_{\mathrm{total}}$ [$\mathrm{kg}$]",labelpad=15,fontsize=18)
    ax_total_fuel[0].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax_total_fuel[0].set_title(rf"$m_{{\mathrm{{total}}}}$ Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {m_total_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {m_total_opt_var:.4e}$",fontsize=24)
    ax_total_fuel[0].legend()

    ax_total_fuel[1].hist(m_fuel_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")

    ax_total_fuel[1].axvline(m_fuel_ci_lower, color='red', linewidth=2,linestyle=':',
               label=rf"CI lower $\approx$ {m_fuel_ci_lower:.4f}")
    ax_total_fuel[1].axvline(m_fuel_ci_upper, color='red', linewidth=2,linestyle=':',
               label=rf"CI upper $\approx$ {m_fuel_ci_upper:.4f}")
    ax_total_fuel[1].axvline(m_fuel_mu, color='red', linewidth=2,linestyle='-',
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {m_fuel_mu:.4f}")

    ax_total_fuel[1].hist(m_fuel_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")

    ax_total_fuel[1].axvline(m_fuel_opt_ci_lower, color='blue', linewidth=2,linestyle=':',
               label=rf"CI lower $\approx$ {m_fuel_opt_ci_lower:.4f}")
    ax_total_fuel[1].axvline(m_fuel_opt_ci_upper, color='blue', linewidth=2,linestyle=':',
               label=rf"CI upper $\approx$ {m_fuel_opt_ci_upper:.4f}")
    ax_total_fuel[1].axvline(m_fuel_opt_mu, color='blue', linewidth=2,linestyle='-',
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {m_fuel_opt_mu:.4f}")

    ax_total_fuel[1].set_xlabel(r"$m_{\mathrm{fuel}}$ [$\mathrm{kg}$]",labelpad=15,fontsize=18)
    ax_total_fuel[1].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax_total_fuel[1].set_title(rf"$m_{{\mathrm{{fuel}}}}$ Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {m_fuel_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {m_fuel_opt_var:.4e}$",fontsize=24)
    ax_total_fuel[1].legend()

    fig_empty_engine, ax_empty_engine = plt.subplots(2, 1, figsize=(14, 14))

    fig_empty_engine.suptitle(
        r"Empty and Engine Mass Probability Distributions",
        fontsize=28
    )

    ax_empty_engine[0].hist(m_empty_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")

    ax_empty_engine[0].axvline(m_empty_ci_lower, color='red', linewidth=2,linestyle=':',
               label=rf"CI lower $\approx$ {m_empty_ci_lower:.4f}")
    ax_empty_engine[0].axvline(m_empty_ci_upper, color='red', linewidth=2,linestyle=':',
               label=rf"CI upper $\approx$ {m_empty_ci_upper:.4f}")
    ax_empty_engine[0].axvline(m_empty_mu, color='red', linewidth=2,linestyle='-',
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {m_empty_mu:.4f}")

    ax_empty_engine[0].hist(m_empty_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")

    ax_empty_engine[0].axvline(m_empty_opt_ci_lower, color='blue', linewidth=2,linestyle=':',
               label=rf"CI lower $\approx$ {m_empty_opt_ci_lower:.4f}")
    ax_empty_engine[0].axvline(m_empty_opt_ci_upper, color='blue', linewidth=2,linestyle=':',
               label=rf"CI upper $\approx$ {m_empty_opt_ci_upper:.4f}")
    ax_empty_engine[0].axvline(m_empty_opt_mu, color='blue', linewidth=2,linestyle='-',
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {m_empty_opt_mu:.4f}")

    ax_empty_engine[0].set_xlabel(r"$m_{\mathrm{empty}}$ [$\mathrm{kg}$]",labelpad=15,fontsize=18)
    ax_empty_engine[0].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax_empty_engine[0].set_title(rf"$m_{{\mathrm{{empty}}}}$ Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {m_empty_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {m_empty_opt_var:.4e}$",fontsize=24)
    ax_empty_engine[0].legend()

    ax_empty_engine[1].hist(m_engine_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")

    ax_empty_engine[1].axvline(m_engine_ci_lower, color='red', linewidth=2,linestyle=':',
               label=rf"CI lower $\approx$ {m_engine_ci_lower:.4f}")
    ax_empty_engine[1].axvline(m_engine_ci_upper, color='red', linewidth=2,linestyle=':',
               label=rf"CI upper $\approx$ {m_engine_ci_upper:.4f}")
    ax_empty_engine[1].axvline(m_engine_mu, color='red', linewidth=2,linestyle='-',
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {m_engine_mu:.4f}")

    ax_empty_engine[1].hist(m_engine_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")

    ax_empty_engine[1].axvline(m_engine_opt_ci_lower, color='blue', linewidth=2,linestyle=':',
               label=rf"CI lower $\approx$ {m_engine_opt_ci_lower:.4f}")
    ax_empty_engine[1].axvline(m_engine_opt_ci_upper, color='blue', linewidth=2,linestyle=':',
               label=rf"CI upper $\approx$ {m_engine_opt_ci_upper:.4f}")
    ax_empty_engine[1].axvline(m_engine_opt_mu, color='blue', linewidth=2,linestyle='-',
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {m_engine_opt_mu:.4f}")

    ax_empty_engine[1].set_xlabel(r"$m_{\mathrm{engine}}$ [$\mathrm{kg}$]",labelpad=15,fontsize=18)
    ax_empty_engine[1].set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax_empty_engine[1].set_title(rf"$m_{{\mathrm{{engine}}}}$ Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {m_engine_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {m_engine_opt_var:.4e}$",fontsize=24)
    ax_empty_engine[1].legend()

    plt.show()

def plot_sfc(dict_response, dict_optimized):

    SFC_dist = dict_response["SFC"]["dist"]
    SFC_ci_lower = dict_response["SFC"]["ci_lower"]
    SFC_ci_upper = dict_response["SFC"]["ci_upper"]
    SFC_mu = dict_response["SFC"]["mu"]
    SFC_var_plus_mu = dict_response["SFC"]["var_plus_mu"]
    SFC_var = dict_response["SFC"]["var"]

    SFC_opt_dist = dict_optimized["SFC"]["dist"]
    SFC_opt_ci_lower = dict_optimized["SFC"]["ci_lower"]
    SFC_opt_ci_upper = dict_optimized["SFC"]["ci_upper"]
    SFC_opt_mu = dict_optimized["SFC"]["mu"]
    SFC_opt_var_plus_mu = dict_optimized["SFC"]["var_plus_mu"]
    SFC_opt_var = dict_optimized["SFC"]["var"]

    fig, ax = plt.subplots(figsize=(14, 7))

    fig.suptitle(
        r"Specific Fuel Consumption Probability Distribution",
        fontsize=28
    )

    ax.hist(SFC_dist,bins=100,density=True,color='red',alpha=0.5,label="response at deterministic optima")
    
    ax.axvline(SFC_ci_lower, color='red', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {SFC_ci_lower:.4e}")
    ax.axvline(SFC_ci_upper, color='red', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {SFC_ci_upper:.4e}")
    ax.axvline(SFC_mu, color='red', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{resp}}}} \ \approx$ {SFC_mu:.4e}")
 
    ax.hist(SFC_opt_dist,bins=100,density=True,color='blue',alpha=0.5,label="optimized probability distribution")
    
    ax.axvline(SFC_opt_ci_lower, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI lower $\approx$ {SFC_opt_ci_lower:.4e}")
    ax.axvline(SFC_opt_ci_upper, color='blue', linewidth=2,linestyle=':', 
               label=rf"CI upper $\approx$ {SFC_opt_ci_upper:.4e}")
    ax.axvline(SFC_opt_mu, color='blue', linewidth=2,linestyle='-', 
               label=rf"$\mu_{{\mathrm{{opt}}}} \ \approx$ {SFC_opt_mu:.4e}")
    
    ax.set_xlabel(r"$\mathrm{SFC}$ [$\frac{\mathrm{kg}}{\mathrm{N} \cdot \mathrm{s}}$]",labelpad=15,fontsize=18)
    ax.set_ylabel(r"Probability Density",labelpad=10,fontsize=18)
    ax.set_title(rf"SFC Distribution: $\sigma^2_{{\mathrm{{resp}}}} = {SFC_var:.4e}, \ \ \sigma^2_{{\mathrm{{opt}}}} = {SFC_opt_var:.4e}$",fontsize=24)
    ax.legend()

    plt.show()

def get_values(prob, copybool = False):
    CL_constraint_dist = prob.get_val('CL_constraint:resampled_responses',copy=copybool).ravel()
    CL_constraint_ci_lower = prob.get_val('CL_constraint:ci_lower',copy=copybool).item()
    CL_constraint_ci_upper = prob.get_val('CL_constraint:ci_upper',copy=copybool).item()
    CL_constraint_mu = prob.get_val('CL_constraint:mean',copy=copybool).item()
    CL_constraint_var_plus_mu = prob.get_val('CL_constraint:mean_plus_var',copy=copybool).item()
    CL_constraint_var = CL_constraint_var_plus_mu - CL_constraint_mu

    CL_constraint = {
        "dist" : CL_constraint_dist,
        "ci_lower" : CL_constraint_ci_lower,
        "ci_upper" : CL_constraint_ci_upper,
        "mu" : CL_constraint_mu,
        "var_plus_mu" : CL_constraint_var_plus_mu,
        "var" : CL_constraint_var
    }

    """
    WL_constraint_dist = prob.get_val('WL_constraint:resampled_responses',copy=copybool).ravel()
    WL_constraint_ci_lower = prob.get_val('WL_constraint:ci_lower',copy=copybool).item()
    WL_constraint_ci_upper = prob.get_val('WL_constraint:ci_upper',copy=copybool).item()
    WL_constraint_mu = prob.get_val('WL_constraint:mean',copy=copybool).item()
    WL_constraint_var_plus_mu = prob.get_val('WL_constraint:mean_plus_var',copy=copybool).item()
    WL_constraint_var = WL_constraint_var_plus_mu - WL_constraint_mu

    WL_constraint = {
        "dist": WL_constraint_dist,
        "ci_lower": WL_constraint_ci_lower,
        "ci_upper": WL_constraint_ci_upper,
        "mu": WL_constraint_mu,
        "var_plus_mu": WL_constraint_var_plus_mu,
        "var": WL_constraint_var,
    }
    """
  

    

    DOC_dist = prob.get_val('DOC:resampled_responses',copy=copybool).ravel()
    DOC_ci_lower = prob.get_val('DOC:ci_lower',copy=copybool).item()
    DOC_ci_upper = prob.get_val('DOC:ci_upper',copy=copybool).item()
    DOC_mu = prob.get_val('DOC:mean',copy=copybool).item()
    DOC_var_plus_mu = prob.get_val('DOC:mean_plus_var',copy=copybool).item()
    DOC_var = DOC_var_plus_mu - DOC_mu

    DOC = {
        "dist": DOC_dist,
        "ci_lower": DOC_ci_lower,
        "ci_upper": DOC_ci_upper,
        "mu": DOC_mu,
        "var_plus_mu": DOC_var_plus_mu,
        "var": DOC_var,
    }

    Dpm_dist = prob.get_val('Dpm:resampled_responses',copy=copybool).ravel()
    Dpm_ci_lower = prob.get_val('Dpm:ci_lower',copy=copybool).item()
    Dpm_ci_upper = prob.get_val('Dpm:ci_upper',copy=copybool).item()
    Dpm_mu = prob.get_val('Dpm:mean',copy=copybool).item()
    Dpm_var_plus_mu = prob.get_val('Dpm:mean_plus_var',copy=copybool).item()
    Dpm_var = Dpm_var_plus_mu - Dpm_mu

    Dpm = {
        "dist": Dpm_dist,
        "ci_lower": Dpm_ci_lower,
        "ci_upper": Dpm_ci_upper,
        "mu": Dpm_mu,
        "var_plus_mu": Dpm_var_plus_mu,
        "var": Dpm_var,
    }
 
    m_fuel_dist = prob.get_val('m_fuel:resampled_responses',copy=copybool).ravel()
    m_fuel_ci_lower = prob.get_val('m_fuel:ci_lower',copy=copybool).item()
    m_fuel_ci_upper = prob.get_val('m_fuel:ci_upper',copy=copybool).item()
    m_fuel_mu = prob.get_val('m_fuel:mean',copy=copybool).item()
    m_fuel_var_plus_mu = prob.get_val('m_fuel:mean_plus_var',copy=copybool).item()
    m_fuel_var = m_fuel_var_plus_mu - m_fuel_mu

    m_fuel = {
        "dist": m_fuel_dist,
        "ci_lower": m_fuel_ci_lower,
        "ci_upper": m_fuel_ci_upper,
        "mu": m_fuel_mu,
        "var_plus_mu": m_fuel_var_plus_mu,
        "var": m_fuel_var,
    }

    m_empty_dist = prob.get_val('m_empty:resampled_responses',copy=copybool).ravel()
    m_empty_ci_lower = prob.get_val('m_empty:ci_lower',copy=copybool).item()
    m_empty_ci_upper = prob.get_val('m_empty:ci_upper',copy=copybool).item()
    m_empty_mu = prob.get_val('m_empty:mean',copy=copybool).item()
    m_empty_var_plus_mu = prob.get_val('m_empty:mean_plus_var',copy=copybool).item()
    m_empty_var = m_empty_var_plus_mu - m_empty_mu

    m_empty = {
        "dist": m_empty_dist,
        "ci_lower": m_empty_ci_lower,
        "ci_upper": m_empty_ci_upper,
        "mu": m_empty_mu,
        "var_plus_mu": m_empty_var_plus_mu,
        "var": m_empty_var,
    }

    m_engine_dist = prob.get_val('m_engine:resampled_responses',copy=copybool).ravel()
    m_engine_ci_lower = prob.get_val('m_engine:ci_lower',copy=copybool).item()
    m_engine_ci_upper = prob.get_val('m_engine:ci_upper',copy=copybool).item()
    m_engine_mu = prob.get_val('m_engine:mean',copy=copybool).item()
    m_engine_var_plus_mu = prob.get_val('m_engine:mean_plus_var',copy=copybool).item()
    m_engine_var = m_engine_var_plus_mu - m_engine_mu

    m_engine = {
        "dist": m_engine_dist,
        "ci_lower": m_engine_ci_lower,
        "ci_upper": m_engine_ci_upper,
        "mu": m_engine_mu,
        "var_plus_mu": m_engine_var_plus_mu,
        "var": m_engine_var,
    }

    m_total_dist = prob.get_val('m_total:resampled_responses',copy=copybool).ravel()
    m_total_ci_lower = prob.get_val('m_total:ci_lower',copy=copybool).item()
    m_total_ci_upper = prob.get_val('m_total:ci_upper',copy=copybool).item()
    m_total_mu = prob.get_val('m_total:mean',copy=copybool).item()
    m_total_var_plus_mu = prob.get_val('m_total:mean_plus_var',copy=copybool).item()
    m_total_var = m_total_var_plus_mu - m_total_mu

    m_total = {
        "dist": m_total_dist,
        "ci_lower": m_total_ci_lower,
        "ci_upper": m_total_ci_upper,
        "mu": m_total_mu,
        "var_plus_mu": m_total_var_plus_mu,
        "var": m_total_var,
    }

    SFC_dist = prob.get_val('SFC:resampled_responses',copy=copybool).ravel()
    SFC_ci_lower = prob.get_val('SFC:ci_lower',copy=copybool).item()
    SFC_ci_upper = prob.get_val('SFC:ci_upper',copy=copybool).item()
    SFC_mu = prob.get_val('SFC:mean',copy=copybool).item()
    SFC_var_plus_mu = prob.get_val('SFC:mean_plus_var',copy=copybool).item()
    SFC_var = SFC_var_plus_mu - SFC_mu
    
    SFC = {
        "dist": SFC_dist,
        "ci_lower": SFC_ci_lower,
        "ci_upper": SFC_ci_upper,
        "mu": SFC_mu,
        "var_plus_mu": SFC_var_plus_mu,
        "var": SFC_var,
    }

    CL_dist = prob.get_val('CL:resampled_responses',copy=copybool).ravel()
    CL_ci_lower = prob.get_val('CL:ci_lower',copy=copybool).item()
    CL_ci_upper = prob.get_val('CL:ci_upper',copy=copybool).item()
    CL_mu = prob.get_val('CL:mean',copy=copybool).item()
    CL_var_plus_mu = prob.get_val('CL:mean_plus_var',copy=copybool).item()
    CL_var = CL_var_plus_mu - CL_mu

    CL = {
        "dist": CL_dist,
        "ci_lower": CL_ci_lower,
        "ci_upper": CL_ci_upper,
        "mu": CL_mu,
        "var_plus_mu": CL_var_plus_mu,
        "var": CL_var,
    }

    CD_dist = prob.get_val('CD:resampled_responses',copy=copybool).ravel()
    CD_ci_lower = prob.get_val('CD:ci_lower',copy=copybool).item()
    CD_ci_upper = prob.get_val('CD:ci_upper',copy=copybool).item()
    CD_mu = prob.get_val('CD:mean',copy=copybool).item()
    CD_var_plus_mu = prob.get_val('CD:mean_plus_var',copy=copybool).item()
    CD_var = CD_var_plus_mu - CD_mu

    CD = {
        "dist": CD_dist,
        "ci_lower": CD_ci_lower,
        "ci_upper": CD_ci_upper,
        "mu": CD_mu,
        "var_plus_mu": CD_var_plus_mu,
        "var": CD_var,
    }

    plotting_vals = {
        "CL_constraint" : CL_constraint,
      #  "WL_constraint" : WL_constraint,
        "DOC" : DOC,
        "Dpm" : Dpm,
        "m_fuel" : m_fuel,
        "m_engine" : m_engine,
        "m_total" : m_total,
        "m_empty" : m_empty,
        "SFC" : SFC,
        "CL" : CL,
        "CD" : CD
    }

    return plotting_vals