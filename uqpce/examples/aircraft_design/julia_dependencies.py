# install_julia_dependencies.py

from juliacall import Main as jl

jl.seval("""
import Pkg

Pkg.add([
    "ADTypes",
    "ComponentArrays",
    "ForwardDiff",
    "OpenMDAOCore",
])
""")