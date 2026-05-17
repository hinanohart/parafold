"""Unit tests for the parafold CLI scaffold."""

from __future__ import annotations

from typer.testing import CliRunner

from parafold import __version__
from parafold.cli import app

runner = CliRunner()


def test_version_command_prints_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


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
    assert "M3" in result.stdout


def test_help_lists_subcommands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "version" in result.stdout
    assert "predict" in result.stdout
