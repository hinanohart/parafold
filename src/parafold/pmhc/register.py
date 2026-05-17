"""Position-aware peptide register.

For class-I (8-11mers) anchors are typically P2 and PΩ (C-terminal).
For class-II (13-25mers) a 9-mer binding core is inferred at M3 fit time;
the placeholder here exposes the full range until the binding-core predictor
ships.
"""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True, slots=True)
class PeptideRegister:
    """The anchor / binding-core positions for a bound peptide."""

    peptide: str
    is_class_one: bool

    def length(self) -> int:
        return len(self.peptide)

    def anchor_positions(self) -> tuple[int, ...]:
        """Return zero-indexed anchor residue positions.

        Class-I: (P2, PΩ) — i.e. ``(1, n-1)``.
        Class-II: full range placeholder until the binding-core head lands at M3.
        """
        n = self.length()
        if n < 2:
            return ()
        if self.is_class_one:
            return (1, n - 1)
        return tuple(range(n))
