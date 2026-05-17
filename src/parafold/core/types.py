"""Shared pydantic models for ParaFold's public surface."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class TCRChainPair(BaseModel):
    """A canonical α/β TCR pair, given as single-letter polypeptide sequences."""

    alpha: str = Field(..., min_length=20, description="TCRα chain")
    beta: str = Field(..., min_length=20, description="TCRβ chain")

    @field_validator("alpha", "beta")
    @classmethod
    def _strip_and_uppercase(cls, value: str) -> str:
        cleaned = value.strip().upper()
        non_aa = set(cleaned) - set("ACDEFGHIKLMNPQRSTVWY")
        if non_aa:
            raise ValueError(
                f"non-standard amino acid letters: {sorted(non_aa)}; use only the 20 "
                "canonical single-letter codes (ACDEFGHIKLMNPQRSTVWY)",
            )
        return cleaned


class pMHCInput(BaseModel):
    """Peptide + HLA allele specification.

    The ``hla`` field accepts both the canonical IPD-IMGT/HLA colon form
    (``HLA-A*02:01``) and the 4-digit IEDB shorthand (``HLA-A*0201``). Locus
    is restricted to the recognised class-I and class-II loci so that nonsense
    locus strings (``HLA-ABCDEF*02:01``) are rejected at the boundary.
    """

    peptide: str = Field(..., min_length=7, max_length=25)
    hla: str = Field(
        ...,
        pattern=(
            r"^HLA-(A|B|C|E|F|G|DRA|DRB[1-9]|DPA[1-9]|DPB[1-9]|DQA[1-9]|DQB[1-9])"
            r"\*(\d{2}:\d{2,3}|\d{4,5})$"
        ),
        description="HLA allele code, e.g. 'HLA-A*02:01' or 'HLA-A*0201'.",
    )

    @field_validator("peptide")
    @classmethod
    def _uppercase_peptide(cls, value: str) -> str:
        return value.strip().upper()


class PredictionResult(BaseModel):
    """The outcome of a single ParaFold complex prediction.

    Note: ``notes`` is restricted to ``dict[str, str]`` for M0-M2 to keep the
    JSON serialisation surface tight. M3 will widen this to
    ``dict[str, str | int | float | bool]`` once the re-ranking head decides
    what numeric metadata to surface; until then callers should encode
    numeric values as strings if they need to round-trip them.
    """

    pdb_path: Path
    confidence: float = Field(..., ge=0.0, le=1.0)
    boltz_version: str
    notes: dict[str, str] = Field(default_factory=dict)
