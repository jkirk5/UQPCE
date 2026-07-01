import numpy as np
import matplotlib.pyplot as plt

from fixed import parameters
from model import initialize
#hi

def p_base_sweep(prob):

    #pbase sweep
    p_base_vector = np.geomspace(1,10,100)
    V_opt = np.zeros(100)
    S_opt = np.zeros(100)
    AR_opt = np.zeros(100)
    SFC_opt = np.zeros(100)
    DOC_opt = np.zeros(100)
    V_init = parameters['V_cruise']

    #enumerate gives idnex and value
    for i, p_base in enumerate(p_base_vector):
        initialize(prob)
        prob.set_val('aircraft.Weight.p_base', p_base)
        prob.run_driver()
        #mdao returns numpy arrays by default
        V_opt[i] = prob.get_val('V')[0]
        S_opt[i] = prob.get_val('S')[0]
        AR_opt[i] = prob.get_val('AR')[0]
        SFC_opt[i] = prob.get_val('SFC_tech')[0]
        DOC_opt[i] = prob.get_val('DOC.DOC')[0]
    
    plt.rcParams.update({
        "text.usetex" : True,
        "font.family" : "serif"
    })

    fig, axes = plt.subplots(2,2)

    ax1 = axes[0] #should be the v plot
    ax2 = axes[1] #should be the SFC plot row

    ax1[0].plot(p_base_vector,AR_opt,label=r"$AR_{\mathrm{opt}}$",color="blue")
    ax1[0].set_xlabel(r"$p_{\mathrm{base}}$")
    ax1[0].set_ylabel(r"$AR_{\mathrm{opt}}]$")
    ax1[0].set_title("Tuning Parameter Sweep: AR Response")
    ax1[0].axhline(y=13,linestyle="--",label=r"$AR_{\mathrm{opt}}$ upper bound",color="orange")
    ax1[0].axhline(y=8,linestyle="--",label=r"$AR_{\mathrm{opt}}$ lower bound",color="red")
    ax1[0].set_xlim(0,50)
    

    ax1LDOC = ax1[0].twinx()
    ax1LDOC.plot(p_base_vector,DOC_opt,label=r"$\mathrm{DOC}$",color="green")
    #ax1LDOC.set_xlabel(r"$p_{\mathrm{base}}$")
    ax1LDOC.set_ylabel(r"$\mathrm{DOC} \ [\frac{\mathrm{USD}}{\mathrm{flight}}]$")

    #combine legends in plot row 0 col 0
    lines_ARL, labels_ARL = ax1[0].get_legend_handles_labels()
    lines_LDOC, labels_LDOC = ax1LDOC.get_legend_handles_labels()

    ax1[0].legend(lines_ARL + lines_LDOC, labels_ARL + labels_LDOC, loc="best")


    ax1[1].plot(p_base_vector,AR_opt,label=r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$",color="blue")
    ax1[1].set_xscale("log",base=2)
    ax1[1].set_xlabel(r"$p_{\mathrm{base}}$")
    ax1[1].set_ylabel(r"$AR_{\mathrm{opt}}$")
    ax1[1].set_title("Tuning Parameter Sweep: AR End Behavior")
    ax1[1].axhline(y=13,linestyle="--",label=r"$AR_{\mathrm{opt}}$ upper bound",color="orange")
    ax1[1].axhline(y=8,linestyle="--",label=r"$AR_{\mathrm{opt}}$ lower bound",color="red")
    ax1[1].legend()

    ax1RDOC = ax1[1].twinx()
    ax1RDOC.plot(p_base_vector,DOC_opt,label=r"$\mathrm{DOC}$",color="green")
    #ax1RDOC.set_xlabel(r"$p_{\mathrm{base}}$")
    ax1RDOC.set_ylabel(r"$\mathrm{DOC} \ [\frac{\mathrm{USD}}{\mathrm{flight}}]$")

    lines_ARR, labels_ARR = ax1[1].get_legend_handles_labels()
    lines_RDOC, labels_RDOC = ax1RDOC.get_legend_handles_labels()

    ax1[1].legend(lines_ARR + lines_RDOC, labels_ARR + labels_RDOC, loc="best")

    ax2[0].plot(p_base_vector,SFC_opt,label=r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$",color="black")
    ax2[0].set_xlabel(r"$p_{\mathrm{base}}$")
    ax2[0].set_ylabel(r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$")
    ax2[0].set_title("Tuning Parameter Sweep: Technology Factor Response")
    ax2[0].axhline(y=1,linestyle="--",label=r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$ upper bound",color="orange")
    ax2[0].axhline(y=0,linestyle="--",label=r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$ initial guess",color="red")    
    ax2[0].set_xlim(0,50)
    #ax2[0].legend()

    ax2LDOC = ax2[0].twinx()
    ax2LDOC.plot(p_base_vector,DOC_opt,label=r"$\mathrm{DOC}$",color="green")
    #ax1LDOC.set_xlabel(r"$p_{\mathrm{base}}$")
    ax2LDOC.set_ylabel(r"$\mathrm{DOC} \ [\frac{\mathrm{USD}}{\mathrm{flight}}]$")

    #combine legends in plot row 0 col 0
    lines2_VL, labels2_VL = ax2[0].get_legend_handles_labels()
    lines2_LDOC, labels2_LDOC = ax2LDOC.get_legend_handles_labels()

    ax2[0].legend(lines2_VL + lines2_LDOC, labels2_VL + labels2_LDOC, loc="best")

    ax2[1].plot(p_base_vector,SFC_opt,label=r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$",color="black")
    ax2[1].set_xscale("log", base=2)
    ax2[1].set_xlabel(r"$p_{\mathrm{base}}$")
    ax2[1].set_ylabel(r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$")
    ax2[1].set_title(r"Tuning Parameter Sweep: $\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$ End Behavior")
    ax2[1].axhline(y=1,linestyle="--",label=r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$ upper bound",color="orange")
    ax2[1].axhline(y=0,linestyle="--",label=r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$ initial guess",color="red")        
    ax2[1].legend()

    ax2RDOC = ax2[1].twinx()
    ax2RDOC.plot(p_base_vector,DOC_opt,label=r"$\mathrm{DOC}$",color="green")
    #ax1LDOC.set_xlabel(r"$p_{\mathrm{base}}$")
    ax2RDOC.set_ylabel(r"$\mathrm{DOC} \ [\frac{\mathrm{USD}}{\mathrm{flight}}]$")

    #combine legends in plot row 0 col 0
    lines2_VR, labels2_VR = ax2[1].get_legend_handles_labels()
    lines2_RDOC, labels2_RDOC = ax2RDOC.get_legend_handles_labels()

    ax2[0].legend(lines2_VR + lines2_RDOC, labels2_VR + labels2_RDOC, loc="best")
    
    plt.show()
    return fig, axes

def ks_sweep(prob):

    ks_vector = np.linspace(5e-5,4e-4,100)
    V_opt = np.zeros(100)
    S_opt = np.zeros(100)
    AR_opt = np.zeros(100)
    SFC_opt = np.zeros(100)
    DOC_opt = np.zeros(100)

    #enumerate gives idnex and value
    for i, ks in enumerate(ks_vector):
        initialize(prob)
        prob.set_val('aircraft.Aero.ks_base', ks)
        prob.run_driver()
        #mdao returns numpy arrays by default
        V_opt[i] = prob.get_val('V')[0]
        S_opt[i] = prob.get_val('S')[0]
        AR_opt[i] = prob.get_val('AR')[0]
        SFC_opt[i] = prob.get_val('SFC_tech')[0]
        DOC_opt[i] = prob.get_val('DOC.DOC')[0]
    
    plt.rcParams.update({
        "text.usetex" : True,
        "font.family" : "serif"
    })
    

    fig, axes = plt.subplots(2,1)

    axV = axes[0]
    axS = axes[1]
    #axAR = axes[2]
    #axSFC = axes[3]
    #axDOC = axes[4]


    axV.plot(ks_vector,V_opt,label=r"$V_{\mathrm{opt}}$",color="blue")
    #axV.set_xscale("log",base=2)
    axV.set_xlabel(r"$\kappa_{s_{\mathrm{base}}}$")
    axV.set_ylabel(r"$V_{\mathrm{opt}} \ [\frac{\mathrm{m}}{\mathrm{s}}]$")
    axV.set_title("Tuning Parameter Sweep: Velocity Response")
    axV.axhline(y=260,linestyle="--",label=r"$V_{\mathrm{opt}}$ upper bound",color="orange")
    axV.axhline(y=parameters["V_cruise"],linestyle="--",label=r"$V_{\mathrm{opt}}$ initial guess",color="red")
    axV.legend()

    axS.plot(ks_vector,SFC_opt,label=r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$",color="blue")
    #axV.set_xscale("log",base=2)
    axS.set_xlabel(r"$\kappa_{s_{\mathrm{base}}}$")
    axS.set_ylabel(r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$")
    axS.set_title("Tuning Parameter Sweep: Technology Factor Response")
    axS.axhline(y=1,linestyle="--",label=r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$ upper bound",color="orange")
    axS.axhline(y=-1,linestyle="--",label=r"$\mathrm{SFC}_{\mathrm{tech}_{\mathrm{opt}}}$ lower bound",color="red")
    axS.legend()

    plt.show()

    return fig, axes

def eta_kv_sweep(prob, grid_size, numlevels=15):
    
    #4 sets of contour figures, sweeping over
    #eta_base and kv_base
    p_base_coarse = [8,9,10,11]
    eta_base = np.linspace(0.0,0.25,grid_size)
    kv_base = np.linspace(0.0,0.25,grid_size)
    eta_grid, kv_grid = np.meshgrid(eta_base, kv_base, indexing='ij')
    
    AR_grid = np.zeros([grid_size,grid_size])
    S_grid = np.zeros([grid_size,grid_size])
    V_grid = np.zeros([grid_size,grid_size])
    SFC_tech_grid = np.zeros([grid_size,grid_size])
    
    plt.rcParams.update({
        "text.usetex" : True,
        "font.family" : "serif"
        })  
    
    #stores the tuples returned by subplot
    plotting_list = []
    
    for plot_index, p_base in enumerate(p_base_coarse):
        plotting_list.append(plt.subplots(2,2))
        for i,eta in enumerate(eta_base):
            for j,kv in enumerate(kv_base):
                initialize(prob)
                prob.set_val('aircraft.Prop.eta_base',val=eta)
                prob.set_val('aircraft.Prop.kv_base',val=kv)
                prob.set_val('aircraft.Weight.p_base',val=p_base)
                prob.run_driver()

                AR_grid[i,j] = prob.get_val('AR')[0]
                S_grid[i,j] = prob.get_val('S')[0]
                V_grid[i,j] = prob.get_val('V')[0]
                SFC_tech_grid[i,j] = prob.get_val('SFC_tech')[0]

        #here python trusts i know what axes is        
        fig, axes = plotting_list[plot_index]

        axAR = axes[0,0] #top left
        axS = axes[0,1] #top right
        axV = axes[1,0] #bottom left
        axSFC_tech = axes[1,1] #bottom left

        #for whole figure title, use fig.suptitle

        fig.suptitle(
                     "Design Optima for Solves of Varying " 
                    r"$\eta_{\mathrm{base}}$ and $\kappa_{v_{\mathrm{base}}}$ "
                    rf" [$p_{{ \mathrm{{base}} }}$ = {p_base}]")

        #apparently rf strings allow variables inserted, with { }, so to keep latex
        #braces you need to double them up

        minAR = np.min(AR_grid)
        maxAR = np.max(AR_grid)
        #levelsAR = np.linspace(minAR,maxAR,numlevels)
        cfAR = axAR.contourf(eta_grid,kv_grid,AR_grid)
        axAR.set_xlabel(r"$\eta_{\mathrm{base}}$")
        axAR.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axAR.set_title(r"Contours of $\mathrm{AR}$")
        fig.colorbar(cfAR,ax=axAR,label=r"$\mathrm{AR}$") #current fig in AR axes

        minS = np.min(S_grid)
        maxS = np.max(S_grid)
        #levelsS = np.linspace(minS,maxS,numlevels)
        cfS = axS.contourf(eta_grid,kv_grid,S_grid)
        axS.set_xlabel(r"$\eta_{\mathrm{base}}$")
        axS.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axS.set_title(r"Contours of $\mathrm{S}$")
        fig.colorbar(cfS,ax=axS,label=r"$\mathrm{S}$") #current fig in S axes

        minV = np.min(V_grid)
        maxV = np.max(V_grid)
        #levelsV = np.linspace(minV,maxV,numlevels)
        cfV = axV.contourf(eta_grid,kv_grid,V_grid)
        axV.set_xlabel(r"$\eta_{\mathrm{base}}$")
        axV.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axV.set_title(r"Contours of $\mathrm{V}$")
        fig.colorbar(cfV,ax=axV,label=r"$\mathrm{V}$") #current fig in V axes

        minSFC_tech = np.min(SFC_tech_grid)
        maxSFC_tech = np.max(SFC_tech_grid)
        #levelsSFC_tech = np.linspace(minSFC_tech,maxSFC_tech,numlevels)
        cfSFC_tech = axSFC_tech.contourf(eta_grid,kv_grid,SFC_tech_grid)
        axSFC_tech.set_xlabel(r"$\eta_{\mathrm{base}}$")
        axSFC_tech.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axSFC_tech.set_title(r"Contours of $\mathrm{SFC_{\mathrm{tech}}}$")
        fig.colorbar(cfSFC_tech,ax=axSFC_tech,label=r"$\mathrm{SFC_{\mathrm{tech}}}$") #current fig in SFC_tech axes


        plt.show() # show every outermost iteration

    return plotting_list
             
def ks_kv_sweep(prob, grid_size, numlevels=30):
    
    #4 sets of contour figures, sweeping over
    #ks_base and kv_base
    p_base_coarse = [3,5,7,9]
    ks_base = np.linspace(0.0,8e-5,grid_size)
    kv_base = np.linspace(0.0,25,grid_size)
    ks_grid, kv_grid = np.meshgrid(ks_base, kv_base, indexing='ij')
    
    AR_grid = np.zeros([grid_size,grid_size])
    S_grid = np.zeros([grid_size,grid_size])
    V_grid = np.zeros([grid_size,grid_size])
    SFC_tech_grid = np.zeros([grid_size,grid_size])
    
    plt.rcParams.update({
        "text.usetex" : True,
        "font.family" : "serif"
        })  
    
    #stores the tuples returned by subplot
    plotting_list = []
    
    for plot_index, p_base in enumerate(p_base_coarse):
        plotting_list.append(plt.subplots(2,2))
        for i,ks in enumerate(ks_base):
            for j,kv in enumerate(kv_base):
                initialize(prob)
                prob.set_val('aircraft.Aero.ks_base',val=ks)
                prob.set_val('aircraft.Prop.kv_base',val=kv)
                prob.set_val('aircraft.Weight.p_base',val=p_base)
                prob.run_driver()

                AR_grid[i,j] = prob.get_val('AR')[0]
                S_grid[i,j] = prob.get_val('S')[0]
                V_grid[i,j] = prob.get_val('V')[0]
                SFC_tech_grid[i,j] = prob.get_val('SFC_tech')[0]

        #here python trusts i know what axes is        
        fig, axes = plotting_list[plot_index]

        axAR = axes[0,0] #top left
        axS = axes[0,1] #top right
        axV = axes[1,0] #bottom left
        axSFC_tech = axes[1,1] #bottom right

        #for whole figure title, use fig.suptitle

        fig.suptitle(
                     "Design Optima for Solves of Varying " 
                    r"$k_{s_{\mathrm{base}}}$ and $\kappa_{v_{\mathrm{base}}}$ "
                    rf" [$p_{{ \mathrm{{base}} }}$ = {p_base}]")

        #apparently rf strings allow variables inserted, with { }, so to keep latex
        #braces you need to double them up

        minAR = np.min(AR_grid)
        maxAR = np.max(AR_grid)
        #levelsAR = np.linspace(minAR,maxAR,numlevels)
        cfAR = axAR.contourf(ks_grid,kv_grid,AR_grid)
        axAR.set_xlabel(r"$k_{s_{\mathrm{base}}}$")
        axAR.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axAR.set_title(r"Contours of $\mathrm{AR}$")
        fig.colorbar(cfAR,ax=axAR,label=r"$\mathrm{AR}$") #current fig in AR axes

        minS = np.min(S_grid)
        maxS = np.max(S_grid)
        #levelsS = np.linspace(minS,maxS,numlevels)
        cfS = axS.contourf(ks_grid,kv_grid,S_grid)
        axS.set_xlabel(r"$k_{s_{\mathrm{base}}}$")
        axS.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axS.set_title(r"Contours of $\mathrm{S}$")
        fig.colorbar(cfS,ax=axS,label=r"$\mathrm{S}$") #current fig in S axes

        minV = np.min(V_grid)
        maxV = np.max(V_grid)
        #levelsV = np.linspace(minV,maxV,numlevels)
        cfV = axV.contourf(ks_grid,kv_grid,V_grid)
        axV.set_xlabel(r"$k_{s_{\mathrm{base}}}$")
        axV.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axV.set_title(r"Contours of $\mathrm{V}$")
        fig.colorbar(cfV,ax=axV,label=r"$\mathrm{V}$") #current fig in V axes

        minSFC_tech = np.min(SFC_tech_grid)
        maxSFC_tech = np.max(SFC_tech_grid)
        #levelsSFC_tech = np.linspace(minSFC_tech,maxSFC_tech,numlevels)
        cfSFC_tech = axSFC_tech.contourf(ks_grid,kv_grid,SFC_tech_grid)
        axSFC_tech.set_xlabel(r"$k_{s_{\mathrm{base}}}$")
        axSFC_tech.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axSFC_tech.set_title(r"Contours of $\mathrm{SFC_{\mathrm{tech}}}$")
        fig.colorbar(cfSFC_tech,ax=axSFC_tech,label=r"$\mathrm{SFC_{\mathrm{tech}}}$") #current fig in SFC_tech axes


    plt.show() # show every outermost iteration

    return plotting_list

def ks_p_sweep(prob, grid_size, numlevels=30):
    
    #4 sets of contour figures, sweeping over
    #ks_base and p_base
    kv_base_coarse = [1,5,9,13,17,21,25]
    ks_base = np.linspace(1e-5,8e-5,grid_size)
    p_base = np.linspace(1.0,13.0,grid_size)
    ks_grid, p_grid = np.meshgrid(ks_base, p_base, indexing='ij')
    
    AR_grid = np.zeros([grid_size,grid_size])
    S_grid = np.zeros([grid_size,grid_size])
    V_grid = np.zeros([grid_size,grid_size])
    SFC_tech_grid = np.zeros([grid_size,grid_size])
    
    plt.rcParams.update({
        "text.usetex" : True,
        "font.family" : "serif"
        })  
    
    #stores the tuples returned by subplot
    plotting_list = []
    
    for plot_index, kv in enumerate(kv_base_coarse):
        plotting_list.append(plt.subplots(2,2))
        for i,ks in enumerate(ks_base):
            for j,p in enumerate(p_base):
                initialize(prob)
                prob.set_val('aircraft.Aero.ks_base',val=ks)
                prob.set_val('aircraft.Weight.p_base',val=p)
                prob.set_val('aircraft.Prop.kv_base',val=kv)
                prob.run_driver()

                AR_grid[i,j] = prob.get_val('AR')[0]
                S_grid[i,j] = prob.get_val('S')[0]
                V_grid[i,j] = prob.get_val('V')[0]
                SFC_tech_grid[i,j] = prob.get_val('SFC_tech')[0]

        #here python trusts i know what axes is        
        fig, axes = plotting_list[plot_index]

        axAR = axes[0,0] #top left
        axS = axes[0,1] #top right
        axV = axes[1,0] #bottom left
        axSFC_tech = axes[1,1] #bottom right

        #for whole figure title, use fig.suptitle

        fig.suptitle(
                     "Design Optima for Solves of Varying " 
                    r"$k_{s_{\mathrm{base}}}$ and $p_{\mathrm{base}}$ "
                    rf" [$\kappa_{{v_{{\mathrm{{base}}}}}}$ = {kv}]")

        #apparently rf strings allow variables inserted, with { }, so to keep latex
        #braces you need to double them up

        minAR = np.min(AR_grid)
        maxAR = np.max(AR_grid)
        #levelsAR = np.linspace(minAR,maxAR,numlevels)
        cfAR = axAR.contourf(ks_grid,p_grid,AR_grid)
        axAR.set_xlabel(r"$k_{s_{\mathrm{base}}}$")
        axAR.set_ylabel(r"$p_{\mathrm{base}}$")
        axAR.set_title(r"Contours of $\mathrm{AR}$")
        fig.colorbar(cfAR,ax=axAR,label=r"$\mathrm{AR}$") #current fig in AR axes

        minS = np.min(S_grid)
        maxS = np.max(S_grid)
        #levelsS = np.linspace(minS,maxS,numlevels)
        cfS = axS.contourf(ks_grid,p_grid,S_grid)
        axS.set_xlabel(r"$k_{s_{\mathrm{base}}}$")
        axS.set_ylabel(r"$p_{\mathrm{base}}$")
        axS.set_title(r"Contours of $\mathrm{S}$")
        fig.colorbar(cfS,ax=axS,label=r"$\mathrm{S}$") #current fig in S axes

        minV = np.min(V_grid)
        maxV = np.max(V_grid)
        #levelsV = np.linspace(minV,maxV,numlevels)
        cfV = axV.contourf(ks_grid,p_grid,V_grid)
        axV.set_xlabel(r"$k_{s_{\mathrm{base}}}$")
        axV.set_ylabel(r"$p_{\mathrm{base}}$")
        axV.set_title(r"Contours of $\mathrm{V}$")
        fig.colorbar(cfV,ax=axV,label=r"$\mathrm{V}$") #current fig in V axes

        minSFC_tech = np.min(SFC_tech_grid)
        maxSFC_tech = np.max(SFC_tech_grid)
        #levelsSFC_tech = np.linspace(minSFC_tech,maxSFC_tech,numlevels)
        cfSFC_tech = axSFC_tech.contourf(ks_grid,p_grid,SFC_tech_grid)
        axSFC_tech.set_xlabel(r"$k_{s_{\mathrm{base}}}$")
        axSFC_tech.set_ylabel(r"$p_{\mathrm{base}}$")
        axSFC_tech.set_title(r"Contours of $\mathrm{SFC_{\mathrm{tech}}}$")
        fig.colorbar(cfSFC_tech,ax=axSFC_tech,label=r"$\mathrm{SFC_{\mathrm{tech}}}$") #current fig in SFC_tech axes


    plt.show() 

    return plotting_list

def p_kv_sweep(prob, grid_size, numlevels=30):
    
    # 4 sets of contour figures, sweeping over
    # p_base and kv_base
    ks_base_coarse = [1e-5,2e-5,3e-5,4e-5 ,5e-5]
    p_base = np.linspace(0.0, 7.0, grid_size)
    kv_base = np.linspace(0.0, 25, grid_size)
    p_grid, kv_grid = np.meshgrid(p_base, kv_base, indexing='ij')
    
    AR_grid = np.zeros([grid_size, grid_size])
    S_grid = np.zeros([grid_size, grid_size])
    V_grid = np.zeros([grid_size, grid_size])
    SFC_tech_grid = np.zeros([grid_size, grid_size])
    
    plt.rcParams.update({
        "text.usetex" : True,
        "font.family" : "serif"
        })  
    
    # stores the tuples returned by subplot
    plotting_list = []
    
    for plot_index, ks in enumerate(ks_base_coarse):
        plotting_list.append(plt.subplots(2, 2))
        for i, p in enumerate(p_base):
            for j, kv in enumerate(kv_base):
                initialize(prob)
                prob.set_val('aircraft.Weight.p_base', val=p)
                prob.set_val('aircraft.Prop.kv_base', val=kv)
                prob.set_val('aircraft.Aero.ks_base', val=ks)
                prob.run_driver()

                AR_grid[i, j] = prob.get_val('AR')[0]
                S_grid[i, j] = prob.get_val('S')[0]
                V_grid[i, j] = prob.get_val('V')[0]
                SFC_tech_grid[i, j] = prob.get_val('SFC_tech')[0]

        # here python trusts i know what axes is        
        fig, axes = plotting_list[plot_index]

        axAR = axes[0, 0] # top left
        axS = axes[0, 1] # top right
        axV = axes[1, 0] # bottom left
        axSFC_tech = axes[1, 1] # bottom right

        # for whole figure title, use fig.suptitle

        fig.suptitle(
                     "Design Optima for Solves of Varying " 
                    r"$p_{\mathrm{base}}$ and $\kappa_{v_{\mathrm{base}}}$ "
                    rf" [$k_{{s_{{\mathrm{{base}}}}}}$ = {ks}]")

        # apparently rf strings allow variables inserted, with { }, so to keep latex
        # braces you need to double them up

        minAR = np.min(AR_grid)
        maxAR = np.max(AR_grid)
        # levelsAR = np.linspace(minAR, maxAR, numlevels)
        cfAR = axAR.contourf(p_grid, kv_grid, AR_grid)
        axAR.set_xlabel(r"$p_{\mathrm{base}}$")
        axAR.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axAR.set_title(r"Contours of $\mathrm{AR}$")
        fig.colorbar(cfAR, ax=axAR, label=r"$\mathrm{AR}$") # current fig in AR axes

        minS = np.min(S_grid)
        maxS = np.max(S_grid)
        # levelsS = np.linspace(minS, maxS, numlevels)
        cfS = axS.contourf(p_grid, kv_grid, S_grid)
        axS.set_xlabel(r"$p_{\mathrm{base}}$")
        axS.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axS.set_title(r"Contours of $\mathrm{S}$")
        fig.colorbar(cfS, ax=axS, label=r"$\mathrm{S}$") # current fig in S axes

        minV = np.min(V_grid)
        maxV = np.max(V_grid)
        # levelsV = np.linspace(minV, maxV, numlevels)
        cfV = axV.contourf(p_grid, kv_grid, V_grid)
        axV.set_xlabel(r"$p_{\mathrm{base}}$")
        axV.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axV.set_title(r"Contours of $\mathrm{V}$")
        fig.colorbar(cfV, ax=axV, label=r"$\mathrm{V}$") # current fig in V axes

        minSFC_tech = np.min(SFC_tech_grid)
        maxSFC_tech = np.max(SFC_tech_grid)
        # levelsSFC_tech = np.linspace(minSFC_tech, maxSFC_tech, numlevels)
        cfSFC_tech = axSFC_tech.contourf(p_grid, kv_grid, SFC_tech_grid)
        axSFC_tech.set_xlabel(r"$p_{\mathrm{base}}$")
        axSFC_tech.set_ylabel(r"$\kappa_{v_{\mathrm{base}}}$")
        axSFC_tech.set_title(r"Contours of $\mathrm{SFC_{\mathrm{tech}}}$")
        fig.colorbar(cfSFC_tech, ax=axSFC_tech, label=r"$\mathrm{SFC_{\mathrm{tech}}}$") # current fig in SFC_tech axes

        plt.show() # show every outermost iteration

    return plotting_list

