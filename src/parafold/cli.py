"""Command-line interface (``parafold``).

Exposes the M0-M2 surface today. M3 wires the ``predict`` command's full
pipeline. This scaffold keeps the entry-point importable from ``pyproject.toml``.
"""

from __future__ import annotations

import typer

from parafold import __version__

app = typer.Typer(
    add_completion=False,
    help="TCR-pMHC repertoire structural predictor.",
)


@app.command("version")
def version_cmd() -> None:
    """Print the installed ParaFold version and exit."""
    typer.echo(__version__)


@app.command("predict")
def predict_cmd(
    tcr_alpha: str = typer.Option(..., "--tcr-alpha", help="TCRα FASTA path"),
    tcr_beta: str = typer.Option(..., "--tcr-beta", help="TCRβ FASTA path"),
    peptide: str = typer.Option(..., "--peptide", help="Peptide single-letter sequence"),
    hla: str = typer.Option(..., "--hla", help="HLA allele code (e.g. 'HLA-A*02:01')"),
    out: str = typer.Option("out.pdb", "--out", help="Output PDB path"),
) -> None:
    """Predict a TCR-pMHC complex. M3 wires the full pipeline."""
    typer.echo("parafold predict: M3 implementation pending — see README roadmap.")
    typer.echo(f"  tcr_alpha={tcr_alpha}")
    typer.echo(f"  tcr_beta={tcr_beta}")
    typer.echo(f"  peptide={peptide}")
    typer.echo(f"  hla={hla}")
    typer.echo(f"  out={out}")
    raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
