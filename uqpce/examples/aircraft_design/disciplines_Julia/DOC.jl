using OpenMDAOCore: OpenMDAOCore
using ComponentArrays: ComponentVector
using ADTypes: ADTypes
using ForwardDiff: ForwardDiff

function DOC_ad(inputs, params)
    DOC_out = ComponentVector(DOC=inputs.Cf_base .* inputs.delta_Cf .* inputs.m_fuel .+ inputs.C_time .* (inputs.R ./ inputs.V_cruise) .+ inputs.k_acq .* inputs.C_eng_ref .* (1 .+ inputs.beta_base .* inputs.delta_beta .* inputs.SFC_tech))
    
    return DOC_out
end

function get_DOC_ad(vector_size::Integer)
    ad_backend = ADTypes.AutoForwardDiff()

    inputs = ComponentVector(
        SFC_tech=1.0,
        V_cruise=1.0,
        R=fill(1.0, vector_size),
        m_fuel=fill(1.0, vector_size),
        delta_Cf=fill(1.0, vector_size),
        delta_beta=fill(1.0, vector_size),
        Cf_base=1.0,
        beta_base=1.0,
        C_time=0.472,
        k_acq=0.00142,
        C_eng_ref=2.2e7
    )

    units_dict = Dict(:V_cruise=>"m/s", :R=>"m", :m_fuel=>"kg", :Cf_base=>"USD/kg", :C_time=>"USD/s", :C_eng_ref=>"USD", :DOC=>"USD")

    comp = OpenMDAOCore.DenseADExplicitComp(ad_backend, DOC_ad, inputs; units_dict=units_dict)
    
    return comp
end