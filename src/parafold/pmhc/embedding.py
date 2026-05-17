"""Allele-conditioned embedding for HLA class-I / class-II contexts.

M3 ships an initial 100-allele table fine-tuned on IEDB; further alleles
fall back to a learned class-I or class-II prototype vector.
"""

from __future__ import annotations

import dataclasses

# Locus tokens are the prefix between ``HLA-`` and ``*`` in the IPD-IMGT
# nomenclature. The input boundary (``pMHCInput`` in ``core/types.py``) only
# admits these tokens; the bare ``"DR"`` / ``"DP"`` / ``"DQ"`` aggregates are
# rejected upstream and would never reach this set.
_CLASS_I_LOCI: frozenset[str] = frozenset({"A", "B", "C", "E", "F", "G"})
_CLASS_II_LOCI: frozenset[str] = frozenset(
    {"DRA", "DRB1", "DRB3", "DRB4", "DRB5", "DPA1", "DPB1", "DQA1", "DQB1"},
)


@dataclasses.dataclass(frozen=True, slots=True)
class HLAEmbedding:
    """A typed handle for an HLA allele plus its locus classification.

    Use :meth:`is_class_one` / :meth:`is_class_two` to gate downstream
    geometry choices (peptide register length, anchor count, etc.).

    M3 reserved signatures
    ----------------------
    The following methods are part of the M3 contract: implementers must
    provide them with this exact return type so callers wired through
    :class:`parafold.pmhc.head.pMHCConditionalHead` keep compiling.

    - ``vector() -> "numpy.ndarray"`` — a fixed-dimension allele embedding
      vector. The M3 implementation reads from a packed ``.npz`` table
      shipped via Hugging Face Hub.
    - ``dim() -> int`` — the embedding dimensionality (constant for a given
      release).

    These are not yet present in the M0-M2 scaffold so that the typed shell
    cannot be mistaken for the trained model. Adding them lands at M3.
    """

    allele: str

    def locus(self) -> str:
        """Return the locus prefix (e.g. ``"A"``, ``"DRB1"``)."""
        return self.allele.removeprefix("HLA-").split("*", 1)[0]

    def is_class_one(self) -> bool:
        return self.locus() in _CLASS_I_LOCI

    def is_class_two(self) -> bool:
        return self.locus() in _CLASS_II_LOCI
