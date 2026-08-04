using OpenMDAOCore: OpenMDAOCore
using ComponentArrays: ComponentVector
using ADTypes: ADTypes
using ForwardDiff: ForwardDiff

function engine_ad(inputs, params)
    engine_out = ComponentVector(m_engine=inputs.m_eng_ref .* (1 .+ inputs.alpha_base .* inputs.delta_alpha .* inputs.SFC_tech))
    
    return engine_out
end

function get_engine_ad(vector_size::Integer)
    ad_backend = ADTypes.AutoForwardDiff()

    inputs = ComponentVector(
        SFC_tech=0.0,
        m_eng_ref=8602.0,
        alpha_base=0.345,
        delta_alpha=fill(1.0, vector_size)
    )

    units_dict = Dict(:m_eng_ref=>"kg", :m_engine=>"kg")

    comp = OpenMDAOCore.DenseADExplicitComp(ad_backend, engine_ad, inputs; units_dict=units_dict)
    
    return comp
end