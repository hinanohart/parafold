"""Unit tests for the Boltz-2 subprocess wrapper."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from parafold.core import BoltzRunner, BoltzRunnerError


class TestBoltzRunner:
    def test_assert_available_raises_when_missing(self) -> None:
        runner = BoltzRunner(executable="definitely-not-on-path-xyz-2026")
        with pytest.raises(BoltzRunnerError, match="not found on PATH"):
            runner.assert_available()

    def test_with_extra_args_is_immutable(self) -> None:
        runner = BoltzRunner()
        extended = runner.with_extra_args("--devices", "1")
        assert runner.extra_args == ()
        assert extended.extra_args == ("--devices", "1")

    def test_run_raises_on_nonzero_exit(self, tmp_path: Path) -> None:
        runner = BoltzRunner(executable="boltz")
        with (
            patch("parafold.core.boltz_runner.shutil.which", return_value="/usr/bin/boltz"),
            patch("parafold.core.boltz_runner.subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=[],
                returncode=1,
                stdout="",
                stderr="boom",
            )
            with pytest.raises(BoltzRunnerError, match="boltz predict failed"):
                runner.run(tmp_path / "input.yaml", tmp_path / "out")

    def test_run_propagates_timeout(self, tmp_path: Path) -> None:
        runner = BoltzRunner(executable="boltz", timeout_seconds=1)
        with (
            patch("parafold.core.boltz_runner.shutil.which", return_value="/usr/bin/boltz"),
            patch("parafold.core.boltz_runner.subprocess.run") as mock_run,
        ):
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="boltz", timeout=1)
            with pytest.raises(BoltzRunnerError, match="timed out"):
                runner.run(tmp_path / "input.yaml", tmp_path / "out")

    def test_run_returns_out_dir_on_success(self, tmp_path: Path) -> None:
        runner = BoltzRunner(executable="boltz")
        out = tmp_path / "out"
        with (
            patch("parafold.core.boltz_runner.shutil.which", return_value="/usr/bin/boltz"),
            patch("parafold.core.boltz_runner.subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="ok",
                stderr="",
            )
            result = runner.run(tmp_path / "input.yaml", out)
        # The mocked argv must use the resolved absolute path, not the bare
        # "boltz" string, so a PATH shim cannot shadow assert_available().
        called_argv = mock_run.call_args.args[0]
        assert called_argv[0] == "/usr/bin/boltz"
        assert result == out
        assert out.is_dir()
