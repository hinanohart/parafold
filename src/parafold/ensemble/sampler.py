"""Reproducible repertoire ensemble sampling.

M4 implements:

1. for each clonotype, draw ``plan.sample_count`` Boltz-2 outputs at distinct seeds,
2. rescore via :class:`parafold.pmhc.head.pMHCConditionalHead`,
3. retain the top-K by re-ranked confidence.

The :class:`SeedPlan` exists so that the sampling schedule is auditable and
trivially reproducible: ``base_seed`` plus ``sample_count`` fully determines
the draw set.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterator


@dataclasses.dataclass(frozen=True, slots=True)
class SeedPlan:
    """A reproducible ensemble sampling plan."""

    base_seed: int
    sample_count: int

    def __post_init__(self) -> None:
        if self.sample_count <= 0:
            raise ValueError("sample_count must be positive")

    def seeds(self) -> Iterator[int]:
        for i in range(self.sample_count):
            yield self.base_seed + i


@dataclasses.dataclass(frozen=True, slots=True)
class RepertoireEnsemble:
    """Top-K seed sampling + rescoring across a TCR repertoire."""

    plan: SeedPlan
    top_k: int = 5

    def __post_init__(self) -> None:
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.top_k > self.plan.sample_count:
            raise ValueError("top_k cannot exceed plan.sample_count")
