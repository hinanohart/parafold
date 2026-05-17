"""ParaFold — TCR-pMHC repertoire structural predictor.

Public re-exports live here so users can ``from parafold import predict_complex``
without reaching into submodules.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("parafold")
except PackageNotFoundError:  # editable install before metadata is built
    __version__ = "0.0.1"

from parafold.core.types import PredictionResult, TCRChainPair, pMHCInput
from parafold.facade import predict_complex

__all__ = [
    "PredictionResult",
    "TCRChainPair",
    "__version__",
    "pMHCInput",
    "predict_complex",
]
