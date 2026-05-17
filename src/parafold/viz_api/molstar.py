"""JSON payload serialisation for Mol* (consumed by the M5 SvelteKit front-end)."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict


class MolstarPayload(TypedDict):
    """The JSON schema consumed by the ParaFold Mol* viewer at M5."""

    url: str
    format: str
    label: str


def structure_to_molstar_payload(pdb_path: Path, label: str) -> MolstarPayload:
    """Serialise a structure path into the JSON Mol* expects.

    Args:
        pdb_path: filesystem path to the predicted complex.
        label: short human-readable label for the viewer's right-hand panel.

    Returns:
        A :class:`MolstarPayload` ready for ``json.dumps``. ``url`` is emitted
        in POSIX form (forward slashes) so the payload round-trips identically
        across Linux, macOS, and Windows producers.
    """
    return MolstarPayload(
        url=pdb_path.as_posix(),
        format="pdb",
        label=label,
    )
