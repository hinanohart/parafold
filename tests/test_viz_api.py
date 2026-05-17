"""Unit tests for the viz_api Mol* JSON exporters."""

from __future__ import annotations

from pathlib import Path

from parafold.viz_api import MolstarPayload, structure_to_molstar_payload


class TestStructureToMolstarPayload:
    def test_payload_round_trip(self) -> None:
        payload = structure_to_molstar_payload(
            pdb_path=Path("/tmp/out.pdb"),
            label="TCR α/β + GILGFVFTL + HLA-A*02:01",
        )
        assert payload["url"] == "/tmp/out.pdb"
        assert payload["format"] == "pdb"
        assert "GILGFVFTL" in payload["label"]

    def test_payload_is_typed_dict(self) -> None:
        payload: MolstarPayload = structure_to_molstar_payload(
            pdb_path=Path("foo.pdb"),
            label="example",
        )
        assert set(payload.keys()) == {"url", "format", "label"}

    def test_relative_path_is_serialised(self) -> None:
        payload = structure_to_molstar_payload(
            pdb_path=Path("predictions") / "complex.pdb",
            label="rel",
        )
        assert payload["url"].endswith("complex.pdb")
