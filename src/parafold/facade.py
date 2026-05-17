"""Top-level facade for the ParaFold public API.

This module owns ``predict_complex`` so the user-facing import surface is
a single name: ``from parafold import predict_complex``.

Pre-M3 the facade performs full input validation and a runner-availability
check, then raises :class:`NotImplementedError` for the YAML emission step.
This keeps the public signature honest about its readiness state.
"""

from __future__ import annotations

import warnings
from pathlib import Path

from pydantic import ValidationError

from parafold.core.boltz_runner import BoltzRunner
from parafold.core.types import PredictionResult, TCRChainPair, pMHCInput


def predict_complex(
    *,
    tcr_alpha: str,
    tcr_beta: str,
    peptide: str,
    hla: str,
    out_dir: Path | None = None,
    runner: BoltzRunner | None = None,
) -> PredictionResult:
    """Predict a TCR α/β + peptide + MHC complex structure.

    Args:
        tcr_alpha: TCRα chain (single-letter polypeptide sequence).
        tcr_beta: TCRβ chain (single-letter polypeptide sequence).
        peptide: bound peptide (typically 8-11 aa for class-I).
        hla: IPD-IMGT/HLA allele code, e.g. ``"HLA-A*02:01"``.
        out_dir: where Boltz-2 should write predictions. **Reserved for M3** —
            until the YAML emitter lands, passing a value raises a
            :class:`FutureWarning` so callers do not assume the path is honoured.
        runner: dependency injection for the Boltz-2 subprocess wrapper.

    Returns:
        A :class:`PredictionResult` referencing the predicted PDB.

    Raises:
        BoltzRunnerError: the upstream predictor failed.
        ValueError: input validation rejected the request.
        NotImplementedError: until M3 ships the pMHC YAML emitter.
    """
    try:
        TCRChainPair(alpha=tcr_alpha, beta=tcr_beta)
    except ValidationError as exc:
        raise ValueError(f"invalid TCR chain pair: {exc}") from exc
    try:
        pMHCInput(peptide=peptide, hla=hla)
    except ValidationError as exc:
        raise ValueError(f"invalid pMHC input: {exc}") from exc

    if out_dir is not None:
        warnings.warn(
            "predict_complex(out_dir=...) is reserved for M3 and currently "
            "ignored. The M3 release wires the YAML emitter and will honour "
            "this path.",
            FutureWarning,
            stacklevel=2,
        )

    runner = runner or BoltzRunner()
    runner.assert_available()

    raise NotImplementedError(
        "predict_complex is wired through M2 (Boltz-2 runner exists) but the "
        "pMHC YAML emitter lands in M3. See the ROADMAP in README.md.",
    )
