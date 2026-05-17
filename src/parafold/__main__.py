"""``python -m parafold`` shim — delegates to :mod:`parafold.cli`."""

from __future__ import annotations

from parafold.cli import app

if __name__ == "__main__":
    app()
