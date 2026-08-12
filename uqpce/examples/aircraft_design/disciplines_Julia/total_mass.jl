using OpenMDAOCore: OpenMDAOCore
using ComponentArrays: ComponentVector
using ADTypes: ADTypes
using ForwardDiff: ForwardDiff

function total_mass_ad(inputs, params)
    total_mass_out = ComponentVector(m_total=inputs.m_empty .+ inputs.m_fuel .+ inputs.m_payload)
    
    return total_mass_out
end

function get_total_mass_ad(vector_size::Integer)
    ad_backend = ADTypes.AutoForwardDiff()

    inputs = ComponentVector(
        m_empty=fill(1.0, vector_size),
        m_fuel=fill(1.0, vector_size),
        m_payload=17955.0
    )

    units_dict = Dict(:m_empty=>"kg", :m_fuel=>"kg", :m_payload=>"kg", :m_total=>"kg")

    comp = OpenMDAOCore.DenseADExplicitComp(ad_backend, total_mass_ad, inputs; units_dict=units_dict)
    
    return comp
end