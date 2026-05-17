# ParaFold

> TCR-pMHC repertoire structural predictor.

ParaFold layers an HLA-allele-conditioned post-processing head and a repertoire
ensemble sampler atop the Boltz-2 base predictor. See the
[README](../README.md) for installation and quickstart.

## Module map

- **`parafold.core`** — Boltz-2 subprocess wrapper and shared pydantic types.
- **`parafold.pmhc`** — HLA allele embedding, peptide register, post-processing head.
- **`parafold.ensemble`** — top-K seed sampling + rescoring across a TCR repertoire.
- **`parafold.viz_api`** — Mol\* JSON exporters and UMAP repertoire projections.

## Readiness

| Module | M0 | M1 | M2 | M3 | M4 | M5 |
|---|---|---|---|---|---|---|
| `core` | ✅ scaffolded | ✅ typed | ✅ runner | — | — | — |
| `pmhc` | — | ✅ scaffolded | ✅ typed | 🔜 trained head | — | — |
| `ensemble` | — | ✅ scaffolded | ✅ typed | — | 🔜 sampling | — |
| `viz_api` | — | ✅ scaffolded | ✅ typed | — | — | 🔜 SvelteKit |

## Design notes

- **No fork of Boltz-2.** ParaFold shells out to the upstream ``boltz`` CLI so
  the version pinning, GPU memory profile, and weight loader remain the user's
  choice. We own only input formatting and output parsing.
- **Frozen dataclasses for the configuration surface.** ``BoltzRunner``,
  ``SeedPlan``, ``RepertoireEnsemble``, ``HLAEmbedding`` are immutable; mutate
  via ``dataclasses.replace`` (exposed as ``with_extra_args`` on the runner).
- **Pydantic for the input boundary.** ``pMHCInput`` and ``TCRChainPair``
  validate at the system boundary; internal modules trust the validated form.
