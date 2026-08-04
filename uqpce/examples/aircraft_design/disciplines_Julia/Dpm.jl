using OpenMDAOCore: OpenMDAOCore
using ComponentArrays: ComponentVector
using ADTypes: ADTypes
using ForwardDiff: ForwardDiff

function Dpm_ad(inputs, params)
    Dpm_out = ComponentVector(Dpm=inputs.DOC ./ (inputs.N_pax .* inputs.R))
    
    return Dpm_out
end

function get_Dpm_ad(vector_size::Integer)
    ad_backend = ADTypes.AutoForwardDiff()

    inputs = ComponentVector(
        R=fill(5.5e3, vector_size),
        DOC=fill(40000.0, vector_size),
        N_pax=189.0
    )

    units_dict = Dict(:R=>"km", :DOC=>"USD")

    comp = OpenMDAOCore.DenseADExplicitComp(ad_backend, Dpm_ad, inputs; units_dict=units_dict)
    
    return comp
end