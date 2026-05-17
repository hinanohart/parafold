"""Unit tests for the top-level facade."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from parafold import predict_complex
from parafold.core import BoltzRunner


class TestPredictComplex:
    def test_rejects_short_peptide(self) -> None:
        with pytest.raises(ValueError, match=r"pMHC|peptide"):
            predict_complex(
                tcr_alpha="Q" * 30,
                tcr_beta="D" * 30,
                peptide="GIL",
                hla="HLA-A*02:01",
            )

    def test_rejects_oversize_peptide(self) -> None:
        """Peptides >25 residues are rejected at the pydantic boundary."""
        with pytest.raises(ValueError, match=r"pMHC|peptide"):
            predict_complex(
                tcr_alpha="Q" * 30,
                tcr_beta="D" * 30,
                peptide="A" * 26,
                hla="HLA-A*02:01",
            )

    def test_rejects_malformed_hla(self) -> None:
        with pytest.raises(ValueError, match=r"pMHC|hla"):
            predict_complex(
                tcr_alpha="Q" * 30,
                tcr_beta="D" * 30,
                peptide="GILGFVFTL",
                hla="A0201",
            )

    def test_m2_explicitly_unready(self, class_one_input: dict[str, str]) -> None:
        """The facade must raise NotImplementedError until M3 ships."""
        with (
            patch.object(BoltzRunner, "assert_available", return_value=None),
            pytest.raises(NotImplementedError, match="M3"),
        ):
            predict_complex(**class_one_input)

    def test_short_tcr_chain_rejected(self) -> None:
        with pytest.raises(ValueError, match=r"TCR chain"):
            predict_complex(
                tcr_alpha="QKVTQ",
                tcr_beta="D" * 30,
                peptide="GILGFVFTL",
                hla="HLA-A*02:01",
            )

    def test_rejects_nonsense_amino_acid_in_tcr(self) -> None:
        """Non-standard amino-acid letters in either TCR chain are rejected."""
        with pytest.raises(ValueError, match=r"TCR chain"):
            predict_complex(
                tcr_alpha=("Q" * 29) + "Z",
                tcr_beta="D" * 30,
                peptide="GILGFVFTL",
                hla="HLA-A*02:01",
            )

    def test_out_dir_emits_future_warning(self, class_one_input: dict[str, str]) -> None:
        """Passing out_dir pre-M3 must emit a FutureWarning, not silently ignore."""
        from pathlib import Path
        from unittest.mock import patch as _patch

        inputs = dict(class_one_input)
        with (
            _patch.object(BoltzRunner, "assert_available", return_value=None),
            pytest.warns(FutureWarning, match=r"out_dir"),
            pytest.raises(NotImplementedError, match="M3"),
        ):
            predict_complex(**inputs, out_dir=Path("/tmp/parafold-out"))

    def test_accepts_iedb_shorthand_hla(self, class_one_input: dict[str, str]) -> None:
        """4-digit IEDB shorthand 'HLA-A*0201' must validate (alongside colon form)."""
        inputs = dict(class_one_input)
        inputs["hla"] = "HLA-A*0201"
        with (
            patch.object(BoltzRunner, "assert_available", return_value=None),
            pytest.raises(NotImplementedError, match="M3"),
        ):
            predict_complex(**inputs)

    def test_rejects_nonsense_hla_locus(self) -> None:
        """The HLA locus is restricted; nonsense locus prefixes must be rejected."""
        with pytest.raises(ValueError, match="hla"):
            predict_complex(
                tcr_alpha="Q" * 30,
                tcr_beta="D" * 30,
                peptide="GILGFVFTL",
                hla="HLA-ZZZ*02:01",
            )

    def test_accepts_class_two_dpb1(self, class_one_input: dict[str, str]) -> None:
        """Class-II DPB1 alleles must validate."""
        inputs = dict(class_one_input)
        inputs["hla"] = "HLA-DPB1*04:01"
        with (
            patch.object(BoltzRunner, "assert_available", return_value=None),
            pytest.raises(NotImplementedError, match="M3"),
        ):
            predict_complex(**inputs)
