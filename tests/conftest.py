"""Shared pytest fixtures for the ParaFold test suite."""

from __future__ import annotations

import pytest

# A canonical influenza M1(58-66) GILGFVFTL / HLA-A*02:01 system used as
# a smoke-test input throughout the suite. Sequences are public benchmarks.
_INFLUENZA_TCR_ALPHA = (
    "QKVTQAQTEISVVEKEDVTLDCVYETRDTTYYLFWYKQPPSGELVFLIRRNSFDEQNEISGRYSWNFQKS"
    "TSSFNFTITASQVVDSAVYFCALSEAEAQGGSEKLVFGKGTKLTVNP"
)
_INFLUENZA_TCR_BETA = (
    "DAGVIQSPRHEVTEMGQEVTLRCKPISGHDYLFWYRQTMMRGLELLIYFNNNVPIDDSGMPEDRFSAKMP"
    "NASFSTLKIQPSEPRDSAVYFCASSLAPGATNEKLFFGSGTQLSVL"
)


@pytest.fixture
def class_one_input() -> dict[str, str]:
    return {
        "tcr_alpha": _INFLUENZA_TCR_ALPHA,
        "tcr_beta": _INFLUENZA_TCR_BETA,
        "peptide": "GILGFVFTL",
        "hla": "HLA-A*02:01",
    }
