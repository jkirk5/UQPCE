using OpenMDAOCore: OpenMDAOCore
using ComponentArrays: ComponentVector
using ADTypes: ADTypes
using ForwardDiff: ForwardDiff

function BreguetRangeComp(X_ca, params)
    R = ((X_ca.V_cruise ./ X_ca.SFC) .* X_ca.LD .* log.(X_ca.m_total ./ (X_ca.m_total .- X_ca.m_fuel)))

    return ComponentVector(R=R)
end

function get_breguet_ad_comp(vec_size::Integer)
    ad_backend = ADTypes.AutoForwardDiff()

    X_ca = ComponentVector(
        V_cruise=231.5,
        SFC = fill(1.60e-4, vec_size),
        LD = fill(16.0, vec_size),
        m_total = fill(50000.0, vec_size),
        m_fuel = fill(10000.0, vec_size)
    )

    units_dict = Dict(
        :V_cruise => "m/s",
        :SFC => "1/s",
        :m_total => "kg",
        :m_fuel => "kg",
        :R => "m",
    )

    return OpenMDAOCore.DenseADExplicitComp(
        ad_backend,
        BreguetRangeComp,
        X_ca;
        params=nothing,
        units_dict=units_dict,
    )
end