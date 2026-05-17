"""ParaFold — TCR-pMHC repertoire structural predictor.

Public re-exports live here so users can ``from parafold import predict_complex``
without reaching into submodules. Pre-M3 the public surface is deliberately
narrow: only ``predict_complex`` and the result model are re-exported. The
``TCRChainPair`` / ``pMHCInput`` boundary models remain importable from
``parafold.core.types`` for advanced callers, but are not part of the M0-M2
stability promise — the M3 release will decide whether they become first-class
inputs to ``predict_complex`` or stay internal.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("parafold")
except PackageNotFoundError:  # editable install before metadata is built
    __version__ = "0+unknown"

from parafold.core.types import PredictionResult
from parafold.facade import predict_complex

__all__ = [
    "PredictionResult",
    "__version__",
    "predict_complex",
]
