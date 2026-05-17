# ParaFold

> TCR-pMHC repertoire structural predictor — Boltz-2 base + HLA-allele-conditioned post-processing head + repertoire ensemble sampling.

[![CI](https://github.com/hinanohart/parafold/actions/workflows/ci.yml/badge.svg)](https://github.com/hinanohart/parafold/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

ParaFold is an open-source Python package for predicting the structural ensemble of T-cell receptor / peptide / MHC complexes. It wraps [Boltz-2](https://github.com/jwohlwend/boltz) as the underlying structure predictor (subprocess; **not** a fork) and contributes:

- An **HLA-allele embedding + peptide register** post-processing head conditioning the predicted complex on class-I/II allele context.
- **Repertoire ensemble sampling** — top-K seed sampling with rescoring across TCR clonotypes, optimised for CDR3 contact-recovery on benchmarks drawn from IEDB / VDJdb / TCR3d.
- A **Mol\* + UMAP** viz layer (M5) for visualising both individual complexes and the projected repertoire space.

> _"What they were calling prediction was closer to auditing — a quiet survey of the sub-space of permutations the protein had already been performing in private."_
> &mdash; ParaFold design notes, internal.

> **Pre-M3 status.** M0-M2 ship the typed scaffold today. Until M3 lands the
> pMHC YAML emitter, the CLI prints a roadmap notice and exits non-zero, and
> the Python API raises `NotImplementedError`. The snippets below are the
> shape of the M3 interface, not the current behaviour.

## Install

```bash
# planned at M3 (not yet on PyPI):
pip install parafold
pip install parafold[torch]   # GPU-side
pip install parafold[umap]    # repertoire space projections

# today (editable install from a clone):
pip install -e ".[dev]"
```

## Quickstart (M3-shaped interface)

```bash
parafold predict \
  --tcr-alpha tcr_a.fa \
  --tcr-beta tcr_b.fa \
  --peptide GILGFVFTL \
  --hla "HLA-A*02:01" \
  --out out.pdb
```

```python
from parafold import predict_complex

# Pre-M3: this call raises NotImplementedError.
# M3+: returns a PredictionResult with pdb_path + confidence.
result = predict_complex(
    tcr_alpha="...",
    tcr_beta="...",
    peptide="GILGFVFTL",
    hla="HLA-A*02:01",
)
print(result.pdb_path, result.confidence)
```

## Architecture

```
parafold/
├── core/        Boltz-2 subprocess wrapper, shared types
├── pmhc/        HLA allele embedding, peptide register, conditional head
├── ensemble/    Repertoire sampling, top-K rescoring
└── viz_api/     Mol* JSON exporters, UMAP projections
```

The base predictor is invoked out-of-process so that Boltz-2 version pinning, dependency surface, and GPU memory profile remain the user's choice. ParaFold layers a typed Python API on top of Boltz-2's command-line interface.

## Roadmap

| Milestone | Scope | Status |
|---|---|---|
| M0 | repo init, license, pyproject | ✅ |
| M1 | module skeleton, typing, tests | ✅ |
| M2 | Boltz-2 subprocess wrapper | ✅ |
| M3 | pMHC module + 1st PyPI release | planned |
| M4 | repertoire ensemble (HF Hub weights) | planned |
| M5 | Mol\* + repertoire UMAP viz | planned |
| M6 | docs + CI | partial (CI only) |
| M7 | tag / arXiv preprint | planned |

## Datasets

ParaFold does **not** redistribute IEDB / VDJdb / TCR3d data. Fine-tuning recipes will fetch from upstream under each provider's own license at M3 release time.

## License

MIT — see [LICENSE](LICENSE).

Upstream component licenses:

| Component | License | Use |
|---|---|---|
| Boltz-2 | MIT | base structure predictor (subprocess) |
| Mol\* | MIT | viz (M5) |
| UMAP-learn | BSD-3 | projection (optional, ``[umap]`` extra) |
| PyTorch | BSD-3 | core (optional, ``[torch]`` extra) |
| Hydra | MIT | config (optional, ``[sci]`` extra) |
| Biotite | BSD-3 | structure I/O (optional, ``[sci]`` extra) |

PHATE (GPL-3) is intentionally **not** used.

> Note: Boltz-2 itself currently requires Linux/CUDA. ParaFold's own typed API
> is OS-agnostic (CI runs on Linux + macOS + Windows), but full structural
> prediction lands when the local Boltz-2 install is available.

## Citation

Preprint forthcoming. See `CITATION.cff` once M3 ships.

## Contributing

Issues and PRs welcome. Run `pytest`, `mypy`, and `ruff` before opening a PR.
