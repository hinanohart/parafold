"""Boltz-2 subprocess wrapper and shared core types.

Design note on the dataclass-vs-pydantic split (deliberate, not accidental):

- ``parafold.core.types`` (``TCRChainPair`` / ``pMHCInput`` / ``PredictionResult``)
  uses **pydantic ``BaseModel``** because these are the *system input boundary*:
  user-supplied amino-acid sequences and HLA codes are validated, normalised
  (strip + upcase), and serialised (JSON, Mol\\* payload) at this layer.
- ``parafold.core.boltz_runner.BoltzRunner``,
  ``parafold.pmhc.{embedding,register,head}``, and
  ``parafold.ensemble.{sampler}`` use **frozen ``@dataclasses.dataclass``
  with ``slots=True``** because they are *internal value objects*: zero
  serialisation surface, all fields trusted (constructed from validated
  pydantic input or library constants), and the immutability + slot layout
  is cheaper than pydantic for a hot inner loop.

In short: pydantic at the public boundary, frozen dataclass behind it.
"""

from __future__ import annotations

from parafold.core.boltz_runner import BoltzRunner, BoltzRunnerError
from parafold.core.types import PredictionResult, TCRChainPair, pMHCInput

__all__ = [
    "BoltzRunner",
    "BoltzRunnerError",
    "PredictionResult",
    "TCRChainPair",
    "pMHCInput",
]
