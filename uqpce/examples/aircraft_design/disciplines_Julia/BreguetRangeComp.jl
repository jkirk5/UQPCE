using OpenMDAOCore: OpenMDAOCore
using ComponentArrays: ComponentVector
using ADTypes: ADTypes
using ForwardDiff: ForwardDiff
using SparseMatrixColorings: SparseMatrixColorings
using SparseConnectivityTracer: SparseConnectivityTracer

function BreguetRangeComp(X_ca, params)
    R = ((X_ca.V_cruise ./ X_ca.SFC) .* X_ca.LD .* log.(X_ca.m_total ./ (X_ca.m_total .- X_ca.m_fuel)))

    return ComponentVector(R=R)
end

function get_breguet_ad_comp(vec_size::Integer)
    ad_backend = ADTypes.AutoSparse(
        ADTypes.AutoForwardDiff(),
        sparsity_detector=SparseConnectivityTracer.TracerSparsityDetector(),
        coloring_algorithm=SparseMatrixColorings.GreedyColoringAlgorithm(),
    )

    X_ca = ComponentVector(
        V_cruise=1.0,
        SFC = fill(1.0, vec_size),
        LD = fill(1.0, vec_size),
        m_total = fill(1.0, vec_size),
        m_fuel = fill(1.0, vec_size)
    )

    units_dict = Dict(
        :V_cruise => "m/s",
        :SFC => "1/s",
        :m_total => "kg",
        :m_fuel => "kg",
        :R => "m",
    )

    return OpenMDAOCore.SparseADExplicitComp(
        ad_backend,
        BreguetRangeComp,
        X_ca;
        params=nothing,
        units_dict=units_dict,
    )
end