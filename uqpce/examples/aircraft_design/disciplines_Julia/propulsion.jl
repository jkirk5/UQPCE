using OpenMDAOCore: OpenMDAOCore

struct Propulsion <: OpenMDAOCore.AbstractExplicitComp
end

function OpenMDAOCore.setup(self::Propulsion)
    inputs = [
        OpenMDAOCore.VarData("SFC_tech", val=0.0),
        OpenMDAOCore.VarData("V_cruise", val=240.5, units="m/s"),
        OpenMDAOCore.VarData("eta_base"),
        OpenMDAOCore.VarData("kv_base"),
        OpenMDAOCore.VarData("delta_eta", val=1.0),
        OpenMDAOCore.VarData("delta_kv", val=1.0),
        OpenMDAOCore.VarData("SFC_ref", val=1.6e-4, units="1/s"),
        OpenMDAOCore.VarData("V_ref", val=231.5, units="m/s")
    ]
    outputs = [
        OpenMDAOCore.VarData("SFC", units="1/s")
    ]
    partials = [
        OpenMDAOCore.PartialsData("SFC", "V_ref"),    
        OpenMDAOCore.PartialsData("SFC", "SFC_ref"),
        OpenMDAOCore.PartialsData("SFC", "SFC_tech"),
        OpenMDAOCore.PartialsData("SFC", "V_cruise"),
        OpenMDAOCore.PartialsData("SFC", "eta_base"),
        OpenMDAOCore.PartialsData("SFC", "kv_base"),
        OpenMDAOCore.PartialsData("SFC", "delta_eta"),
        OpenMDAOCore.PartialsData("SFC", "delta_kv")
    ]
    # @show partials
    return inputs, outputs, partials
end

function OpenMDAOCore.compute!(self::Propulsion, inputs, outputs)
    SFC_ref = inputs["SFC_ref"][1]
    eta_base = inputs["eta_base"][1]
    kv_base = inputs["kv_base"][1]
    V_ref = inputs["V_ref"][1]
    SFC_tech = inputs["SFC_tech"][1]
    V_cruise = inputs["V_cruise"][1]
    delta_eta = inputs["delta_eta"][1]
    delta_kv = inputs["delta_kv"][1]

    outputs["SFC"][1] = SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)^2)

    return nothing
end

function OpenMDAOCore.compute_partials!(self::Propulsion, inputs, partials)
    # @show keys(partials)
    
    SFC_ref = inputs["SFC_ref"][1]
    eta_base = inputs["eta_base"][1]
    kv_base = inputs["kv_base"][1]
    V_ref = inputs["V_ref"][1]
    SFC_tech = inputs["SFC_tech"][1]
    V_cruise = inputs["V_cruise"][1]
    delta_eta = inputs["delta_eta"][1]
    delta_kv = inputs["delta_kv"][1]

    partials["SFC", "SFC_tech"][1] = SFC_ref * (-eta_base * delta_eta) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)^2)
    partials["SFC", "V_cruise"][1] = (2 / V_ref) * (SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (kv_base * delta_kv * (V_cruise/V_ref - 1)))
    
    partials["SFC", "SFC_ref"][1] = (1 - eta_base * delta_eta * SFC_tech) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)^2)
    partials["SFC", "eta_base"][1] = SFC_ref * (-delta_eta * SFC_tech) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)^2)
    partials["SFC", "kv_base"][1] = SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (delta_kv * (V_cruise/V_ref - 1)^2)
    partials["SFC", "V_ref"][1] = (-2 * V_cruise / V_ref^2) * (SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (kv_base * delta_kv * (V_cruise/V_ref - 1)))

    partials["SFC", "delta_eta"][1] = SFC_ref * (-eta_base * SFC_tech) * (1 + kv_base * delta_kv * (V_cruise/V_ref - 1)^2)
    partials["SFC", "delta_kv"][1] = SFC_ref * (1 - eta_base * delta_eta * SFC_tech) * (kv_base * (V_cruise/V_ref - 1)^2)

    return nothing
end

using ComponentArrays: ComponentVector
using ADTypes: ADTypes
using ForwardDiff: ForwardDiff
using SparseMatrixColorings: SparseMatrixColorings
using SparseConnectivityTracer: SparseConnectivityTracer

function propulsion_ad(inputs, params)
    SFC_out = ComponentVector(SFC=inputs.SFC_ref .* (1 .- inputs.eta_base .* inputs.delta_eta .* inputs.SFC_tech) .* (1 .+ inputs.kv_base .* inputs.delta_kv .* (inputs.V_cruise ./ inputs.V_ref .- 1).^2))
    
    return SFC_out
end

function get_prop_ad(vector_size::Integer)
    ad_backend = ADTypes.AutoSparse(
        ADTypes.AutoForwardDiff(),
        sparsity_detector=SparseConnectivityTracer.TracerSparsityDetector(),
        coloring_algorithm=SparseMatrixColorings.GreedyColoringAlgorithm(),
    )

    inputs = ComponentVector(
        SFC_tech=1.0,
        V_cruise=1.0,
        eta_base=1.0,
        kv_base=1.0,
        delta_eta=fill(1.0, vector_size),
        delta_kv=fill(1.0, vector_size),
        SFC_ref=1.6e-4,
        V_ref=231.5
    )

    units_dict = Dict(:V_cruise=>"m/s", :SFC_ref=>"1/s", :V_ref=>"m/s", :SFC=>"1/s")

    comp = OpenMDAOCore.SparseADExplicitComp(ad_backend, propulsion_ad, inputs; units_dict=units_dict)
    
    return comp
end