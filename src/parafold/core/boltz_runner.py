"""Subprocess wrapper around the upstream ``boltz`` CLI.

ParaFold deliberately does not fork Boltz-2 nor link it as a Python import.
The runner shells out to ``boltz predict`` so that upstream version pinning,
GPU-memory profile, and weight loading remain under the user's control.
ParaFold owns input formatting and output parsing only.
"""

from __future__ import annotations

import dataclasses
import shutil
import subprocess
from pathlib import Path


class BoltzRunnerError(RuntimeError):
    """Raised when the upstream ``boltz`` CLI fails or is missing."""


@dataclasses.dataclass(frozen=True, slots=True)
class BoltzRunner:
    """A thin, frozen wrapper that invokes ``boltz predict`` out-of-process."""

    executable: str = "boltz"
    extra_args: tuple[str, ...] = ()
    timeout_seconds: int = 3600

    def _resolved_executable(self) -> str:
        """Return the absolute path of ``self.executable`` on PATH, or die."""
        resolved = shutil.which(self.executable)
        if resolved is None:
            raise BoltzRunnerError(
                f"upstream executable {self.executable!r} not found on PATH; "
                "install it via `pip install boltz` or pass a different path",
            )
        return resolved

    def assert_available(self) -> None:
        """Raise :class:`BoltzRunnerError` if the executable is not on PATH."""
        self._resolved_executable()

    def run(self, yaml_input: Path, out_dir: Path) -> Path:
        """Run ``boltz predict`` and return the populated output directory.

        Args:
            yaml_input: a Boltz-2 input YAML describing chains + ligands.
            out_dir: directory the predictor should populate (created if absent).

        Returns:
            The same ``out_dir`` (for chaining).

        Raises:
            BoltzRunnerError: non-zero exit or timeout.
        """
        out_dir.mkdir(parents=True, exist_ok=True)
        # Resolve to an absolute path so a `boltz` shim earlier in CWD or PATH
        # cannot silently shadow the installed executable between
        # `assert_available()` and the actual run.
        executable = self._resolved_executable()
        argv: list[str] = [
            executable,
            "predict",
            str(yaml_input),
            "--out_dir",
            str(out_dir),
            *self.extra_args,
        ]
        try:
            completed = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise BoltzRunnerError(
                f"boltz predict timed out after {self.timeout_seconds}s",
            ) from exc

        if completed.returncode != 0:
            if completed.stderr:
                # Keep the last ~50 lines of upstream stderr so ANSI-noisy
                # progress bars do not eclipse the actual error.
                lines = completed.stderr.splitlines()
                tail = "\n".join(lines[-50:]) if lines else "(no stderr)"
            else:
                tail = "(no stderr)"
            raise BoltzRunnerError(
                f"boltz predict failed (rc={completed.returncode}):\n--- stderr ---\n{tail}",
            )
        return out_dir

    def with_extra_args(self, *args: str) -> BoltzRunner:
        """Return a copy with additional argv tokens appended."""
        return dataclasses.replace(self, extra_args=(*self.extra_args, *args))
