using ADTypes: ADTypes
using ComponentArrays: ComponentVector
using ForwardDiff: ForwardDiff
using OpenMDAOCore: OpenMDAOCore

function aero!(outputs,inputs,params)
    
    S = @view inputs[:S]
    V_cruise = @view inputs[:V_cruise]
    AR = @view inputs[:AR]

    #model variable (output from other component)
    m_total = @view inputs[:m_total]

    #uncertain parameters
    delta_CD0 = @view inputs[:delta_CD0]
    delta_ks = @view inputs[:delta_ks]
    delta_e = @view inputs[:delta_e]

    #tuning parameters
    ks_base = @view inputs[:ks_base]
    e_base = @view inputs[:e_base]
    C_D0_base = @view inputs[:C_D0_base]


    #constant parameters, will use inputs here for now, but params later?
    g = @view inputs[:g]
    rho = @view inputs[:rho]
    S_0 = @view inputs[:S_0]

    CL = @view outputs[:CL]
    CD = @view outputs[:CD]
    LD = @view outputs[:LD]
    WL = @view outputs[:WL]

    @. CL = (m_total * g) / (0.5 * S * rho * V_cruise^2)

    @. CD = (
    C_D0_base * delta_CD0
    + ks_base * delta_ks * (S - S_0)
    + CL^2 / (π * AR * e_base * delta_e)
    )

    @. LD = CL / CD
    @. WL = (m_total * g) / S

    return nothing
end

function get_aero_comp(vec_size::Integer)

    ad_backend = ADTypes.AutoForwardDiff()

    inputs = ComponentVector(
        S = 1.0,
        V_cruise = 1.0,
        AR = 1.0,
        m_total = ones(vec_size),
        delta_CD0 = ones(vec_size),
        delta_ks = ones(vec_size),
        delta_e = ones(vec_size),
        ks_base = 1.0,
        e_base = 1.0,
        C_D0_base = 1.0,
        g = 9.81,
        rho = 0.38,
        S_0 = 124.58
    )

    outputs = ComponentVector(
        CL = zeros(vec_size),
        CD = zeros(vec_size),
        LD = zeros(vec_size),
        WL = zeros(vec_size))

    units_dict = Dict(
    :S         => "m**2",
    :V_cruise  => "m/s",
    :m_total   => "kg",
    :ks_base   => "1/m**2",
    :g         => "m/s**2",
    :rho       => "kg/m**3",
    :S_0       => "m**2",
    :WL        => "N/m**2",
    :CL        => "unitless",
    :CD        => "unitless",
    :LD        => "unitless"
    )

    return OpenMDAOCore.DenseADExplicitComp(
        ad_backend, aero!, outputs, inputs, units_dict=units_dict)
end