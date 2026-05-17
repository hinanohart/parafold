# Changelog

All notable changes to ParaFold are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
follows [Semantic Versioning](https://semver.org/). Versions below 0.1.0 are
pre-alpha; the public API may break without deprecation cycles until M3.

## [0.0.4] — 2026-05-18

### Changed
- README contribution bullets rewritten in subjunctive ("will provide" /
  "to be evaluated") with explicit milestone tags, so the M0-M2 scaffold is
  no longer described as if it already implemented HLA conditioning,
  ensemble rescoring, or benchmark optimisation.
- ``parafold.__all__`` shrinks to the M0-M2 stable surface
  (``predict_complex``, ``PredictionResult``, ``__version__``). The
  ``TCRChainPair`` and ``pMHCInput`` boundary models are still importable
  from ``parafold.core.types`` but are not part of the public re-export
  surface — ``predict_complex`` consumes raw strings on purpose, and the
  pydantic models are an internal validation detail until M3 decides on the
  final input shape.
- ``parafold`` CLI ``--tcr-alpha`` / ``--tcr-beta`` / ``--peptide`` help
  strings now describe single-letter polypeptide sequences (matching the
  facade), not FASTA paths.
- ``BoltzRunner`` resolves the executable via ``shutil.which`` once and
  invokes the resulting absolute path, so a ``boltz`` shim earlier on the
  caller's ``PATH`` does not silently take over.
- ``predict_complex`` error message for non-canonical amino acids now lists
  the 20 canonical letters as an actionable hint.

### Added
- ``CHANGELOG.md`` (this file). ``scripts/release.sh`` release notes now
  point at it explicitly.
- ``.pre-commit-config.yaml`` runs ruff-check, ruff-format, mypy, and
  trailing-whitespace / end-of-file fixers; ``CONTRIBUTING.md`` documents the
  one-time ``pre-commit install``.
- M3 signature pre-commitment docstrings on ``HLAEmbedding``,
  ``PeptideRegister``, ``pMHCConditionalHead``, ``RepertoireEnsemble`` so
  M3 implementers know which method signatures the scaffold reserves vs.
  which are free to redesign.
- ``parafold/core/__init__.py`` documents the deliberate pydantic
  (input boundary) / frozen dataclass (internal value object) split.
- ``tests/test_facade.py`` and ``tests/test_pmhc.py`` cover max-length
  peptide rejection, parameterised HLA edge cases, and ``out_dir``
  ``FutureWarning`` (added in v0.0.2 but lacked a coverage assertion).
- ``INSTRUCTIONS_MANUAL.md`` M7 section now cross-references "release
  preprint simultaneously with M3 PyPI cut", per the architecture memory.

### Fixed
- ``scripts/release.sh``: ``cmd_all`` now builds exactly once and reuses
  ``dist/`` across ``gh-release`` and ``pypi``, so the artefacts uploaded to
  the two channels are byte-identical. ``cmd_all`` also fails fast if
  ``TWINE_PASSWORD`` is missing, before any GitHub Release is created.
  ``cmd_gh_release`` refuses to run if the current commit is not tagged at
  ``v$(current_version)``, and re-writes title + notes on each invocation
  for true idempotency. ``cmd_hf_hub`` passes the token through
  ``HUGGING_FACE_HUB_TOKEN`` instead of ``--token`` so it never appears in
  ``ps aux``.
- ``[tool.coverage.run].omit`` excludes ``src/parafold/__main__.py`` so the
  reported coverage reflects the tested surface honestly.

## [0.0.3] — 2026-05-17

### Fixed
- ``parafold.viz_api.structure_to_molstar_payload`` emits ``Path.as_posix()``
  for the ``url`` field. Windows runners had been normalising
  ``Path("/tmp/out.pdb")`` to ``\tmp\out.pdb``; the payload now round-trips
  identically on Linux, macOS, and Windows.

## [0.0.2] — 2026-05-17

### Changed
- Owner of the public repo migrated from ``runza/`` to ``hinanohart/``.
  ``CITATION.cff`` and ``CONTRIBUTING.md`` URLs corrected so academic citation
  parsers and the contributor onboarding clone step both resolve.
- Runtime dependencies trimmed from seven to two (``pydantic``, ``typer``).
  The scientific stack (``numpy`` / ``scipy`` / ``biotite`` / ``hydra-core``)
  is now an opt-in ``[sci]`` extra. Pre-M3 install size drops from 200 MB+
  to a few megabytes.
- CI matrix expands to Ubuntu + macOS + Windows × Python 3.11 / 3.12, with
  a separate ``build`` job that ``python -m build`` and import-tests the
  resulting wheel.
- Shell defaults pinned to ``bash -euo pipefail``.

### Added
- ``experiments/_wip/`` is now ``.gitignore``-protected (only ``.gitkeep``
  and a README tracked) so failure-recovery cp -r snapshots cannot leak.
- ``predict_complex(out_dir=...)`` emits ``FutureWarning`` instead of
  silently ignoring the path.
- ``docs/index.md`` records four open architectural uncertainties and the
  M3-M7 release boundary policy.
- ``scripts/release.sh`` (build / pypi / gh-release / hf-hub / docs / all)
  and ``INSTRUCTIONS_MANUAL.md`` enumerate every step that cannot be scripted.
- ``.github/dependabot.yml`` watches GitHub Actions + pip with weekly
  batched PRs.
- ``pyproject.toml`` coverage configuration with ``--cov-fail-under=85``.

### Fixed
- ``BoltzRunner`` stderr tail switched from "last 2000 bytes" to "last 50
  lines" so ANSI-noisy progress bars do not eclipse the real error.
- ``parafold.cli`` diagnostics route through stderr (UNIX convention).
- ``pmhc.embedding`` class-II locus set drops the dead aggregates
  (``"DR"``, ``"DP"``, ``"DQ"``) that the input regex never emits.
- ``__version__`` fallback for editable installs reads ``"0+unknown"``
  instead of a hardcoded ``"0.0.1"`` that drifted from ``pyproject.toml``.

## [0.0.1] — 2026-05-17

### Added
- Initial M0-M2 scaffold: typed Python API, ``BoltzRunner`` subprocess
  wrapper, pydantic input boundary, ``parafold`` CLI scaffold, Mol\* JSON
  exporter, 34 unit tests, ruff + mypy strict CI on Python 3.11 / 3.12.

[0.0.4]: https://github.com/hinanohart/parafold/releases/tag/v0.0.4
[0.0.3]: https://github.com/hinanohart/parafold/releases/tag/v0.0.3
[0.0.2]: https://github.com/hinanohart/parafold/releases/tag/v0.0.2
[0.0.1]: https://github.com/hinanohart/parafold/releases/tag/v0.0.1
