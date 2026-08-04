using OpenMDAOCore: OpenMDAOCore
using ComponentArrays: ComponentVector
using ADTypes: ADTypes
using ForwardDiff: ForwardDiff

function WeightsComp(X_ca, params)
    m_wing = (X_ca.kw_base .* X_ca.delta_kw .* X_ca.S^0.758 .* X_ca.AR^0.6 .* X_ca.m_total .^ 0.006 .* (X_ca.V / X_ca.V_ref).^(X_ca.p_base .* X_ca.delta_p))
    m_empty = (m_wing .+ X_ca.m_fuse .+ X_ca.fsys_base .* X_ca.m_total .* X_ca.delta_fsys .+ X_ca.m_engine)

    return ComponentVector(m_empty = m_empty, m_wing = m_wing)
end

function get_weights_ad_comp(vec_size:: Integer)
    ad_backend = ADTypes.AutoForwardDiff()

    X_ca = ComponentVector(
        S = 124.58,
        AR = 34.32^2 / 124.58,
        V = 231.5,

        m_total = fill(50000.0, vec_size),
        m_engine = fill(8602.0, vec_size),

        delta_kw = fill(1.0, vec_size),
        delta_fsys = fill(1.0, vec_size),
        delta_p = fill(1.0, vec_size),

        kw_base = 53.0,
        fsys_base = 0.19357,
        p_base = 5.3,
        V_ref = 231.5,
        m_fuse = 14518.0
    )

    units_dict = Dict(
        :S => "m**2"
        :V => "m/s",
        :m_total => "kg",
        :m_engine => "kg",
        :V_ref => "m/s",
        :m_fuse => "kg",
        :m_empty => "kg",
        :m_wing => "kg",
    )

    return OpenMDAOCore.DenseADExplicitComp(
        ad_backend,
        WeightsComp,
        X_ca,
        params= nothing
    )
end