"""Unit tests for repertoire ensemble sampling."""

from __future__ import annotations

import pytest

from parafold.ensemble import RepertoireEnsemble, SeedPlan


class TestSeedPlan:
    def test_seeds_are_deterministic(self) -> None:
        plan = SeedPlan(base_seed=42, sample_count=4)
        assert list(plan.seeds()) == [42, 43, 44, 45]

    def test_rejects_zero_sample_count(self) -> None:
        with pytest.raises(ValueError, match="sample_count"):
            SeedPlan(base_seed=0, sample_count=0)


class TestRepertoireEnsemble:
    def test_rejects_top_k_zero(self) -> None:
        with pytest.raises(ValueError, match="top_k must be positive"):
            RepertoireEnsemble(plan=SeedPlan(0, 4), top_k=0)

    def test_rejects_top_k_larger_than_samples(self) -> None:
        with pytest.raises(ValueError, match="exceed"):
            RepertoireEnsemble(plan=SeedPlan(0, 4), top_k=10)

    def test_accepts_valid_top_k(self) -> None:
        ens = RepertoireEnsemble(plan=SeedPlan(0, 8), top_k=3)
        assert ens.top_k == 3
        assert ens.plan.sample_count == 8
