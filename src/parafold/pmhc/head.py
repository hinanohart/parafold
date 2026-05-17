"""Post-processing head that re-ranks Boltz-2 outputs.

The head is a small learned function (trained at M3) consuming:
  - per-residue confidences from the Boltz-2 prediction JSON,
  - the :class:`HLAEmbedding` for the bound allele,
  - the :class:`PeptideRegister` for anchor / binding-core geometry,
and producing a re-ranked confidence plus a suggested contact mask over the
TCR CDR loops.
"""

from __future__ import annotations

import dataclasses

from parafold.pmhc.embedding import HLAEmbedding
from parafold.pmhc.register import PeptideRegister


@dataclasses.dataclass(frozen=True, slots=True)
class pMHCConditionalHead:
    """Allele + register-conditioned re-ranking head.

    Pre-M3 this is a typed placeholder: :meth:`is_ready` returns ``False`` until
    trained weights ship via Hugging Face Hub at M4.
    """

    embedding: HLAEmbedding
    register: PeptideRegister

    def is_ready(self) -> bool:
        """Return ``True`` once trained weights are loadable. Always ``False`` pre-M3."""
        return False
