# Contributing to ParaFold

Thanks for your interest. ParaFold is pre-M3 — the public API surface is small
on purpose and will firm up at the first PyPI release.

## Development setup

```bash
git clone https://github.com/hinanohart/parafold
cd parafold
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,docs]"
```

## Release cadence

Releases beyond M2 are not automated end-to-end. PyPI (M3), Hugging Face Hub
(M4) and the arXiv preprint (M7) each require credentials that live outside
the repository; maintainers cut them manually. See `scripts/release.sh` and
`INSTRUCTIONS_MANUAL.md` for the exact split between scripted and human-only
steps.

## Quality gates

Before opening a PR please run:

```bash
ruff check .
mypy src
pytest --cov=parafold
```

CI runs the same three gates on Python 3.11 and 3.12.

## Scope

| Welcome | Out of scope (for now) |
|---|---|
| bug fixes, test coverage, doc improvements | new fold-prediction backends (Boltz-2 is the chosen base through M5) |
| typing / mypy strict fixes | features that would block at M3 — open an issue first |
| new HLA class-II coverage tests | UI work — wait for M5 SvelteKit scaffold |
| benchmark scripts targeting IEDB / VDJdb | redistributing IEDB / VDJdb data (license, never) |

## Commit messages

Plain English. No internal rule IDs in commit messages. Reference issues by
number; explain the **why** in the body when the **what** is non-obvious.

## License

By contributing you agree your contribution is licensed under the MIT license
of the project (see [LICENSE](LICENSE)).
