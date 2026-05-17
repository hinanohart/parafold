"""Unit tests for the pMHC post-processing components."""

from __future__ import annotations

import pytest

from parafold.pmhc import HLAEmbedding, PeptideRegister, pMHCConditionalHead


class TestHLAEmbedding:
    @pytest.mark.parametrize("allele", ["HLA-A*02:01", "HLA-B*07:02", "HLA-C*04:01"])
    def test_class_one_alleles(self, allele: str) -> None:
        emb = HLAEmbedding(allele=allele)
        assert emb.is_class_one()
        assert not emb.is_class_two()

    @pytest.mark.parametrize(
        "allele",
        ["HLA-DRB1*03:01", "HLA-DQA1*05:01", "HLA-DPB1*04:02"],
    )
    def test_class_two_alleles(self, allele: str) -> None:
        emb = HLAEmbedding(allele=allele)
        assert emb.is_class_two()
        assert not emb.is_class_one()

    def test_locus_extraction(self) -> None:
        assert HLAEmbedding(allele="HLA-A*02:01").locus() == "A"
        assert HLAEmbedding(allele="HLA-DRB1*15:01").locus() == "DRB1"


class TestPeptideRegister:
    def test_class_one_anchors(self) -> None:
        reg = PeptideRegister(peptide="GILGFVFTL", is_class_one=True)
        assert reg.anchor_positions() == (1, 8)
        assert reg.length() == 9

    def test_class_two_returns_full_range(self) -> None:
        reg = PeptideRegister(peptide="AAYFPGAVRGI", is_class_one=False)
        anchors = reg.anchor_positions()
        assert len(anchors) == 11

    def test_one_residue_peptide_has_no_anchors(self) -> None:
        reg = PeptideRegister(peptide="G", is_class_one=True)
        assert reg.anchor_positions() == ()


class TestpMHCConditionalHead:
    def test_head_not_ready_before_m3(self) -> None:
        head = pMHCConditionalHead(
            embedding=HLAEmbedding(allele="HLA-A*02:01"),
            register=PeptideRegister(peptide="GILGFVFTL", is_class_one=True),
        )
        assert head.is_ready() is False
