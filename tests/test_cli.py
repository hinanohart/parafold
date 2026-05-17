"""Unit tests for the parafold CLI scaffold."""

from __future__ import annotations

from typer.testing import CliRunner

from parafold import __version__
from parafold.cli import app

# result.output is the combined stdout+stderr stream. Recent Click (≥8.2)
# removed the mix_stderr kwarg and exposes only combined output to invokers.
runner = CliRunner()


def test_version_command_prints_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_predict_command_exits_2_pre_m3() -> None:
    """The predict CLI is a scaffold pre-M3 and must exit non-zero loudly."""
    result = runner.invoke(
        app,
        [
            "predict",
            "--tcr-alpha",
            "tcr_a.fa",
            "--tcr-beta",
            "tcr_b.fa",
            "--peptide",
            "GILGFVFTL",
            "--hla",
            "HLA-A*02:01",
        ],
    )
    assert result.exit_code == 2
    # The diagnostic flows through typer.echo(..., err=True) — visible in the
    # combined Result.output stream.
    assert "M3" in result.output


def test_help_lists_subcommands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "version" in result.output
    assert "predict" in result.output
