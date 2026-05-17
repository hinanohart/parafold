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

## Open questions (pre-M3)

The following architectural assumptions are recorded as open and will be
re-evaluated at the M3 cut. They are documented here so downstream readers
do not infer that the M0-M2 scaffold has already settled them.

1. **Boltz-2 multi-chain API.** Whether the upstream ``boltz`` CLI accepts
   four-chain input (TCRα + TCRβ + peptide + MHC) in a single YAML, or
   whether ParaFold must split into pairwise predictions and stitch, is
   verified at M3 against the current Boltz-2 release.
2. **Fine-tune compute envelope.** The A100-hour cost of fine-tuning Boltz-2
   on IEDB / VDJdb is not yet measured. A 100-step dry-run at M4 establishes
   per-step memory and wall-clock; a blocker here pushes ensemble release.
3. **Niche differentiation.** TCRdock, TCRmodel2, and ImmuneFold occupy
   adjacent niches. The benchmark suite at M3 will quantify the CDR3
   contact-recovery delta; if the margin is inside noise we re-scope.
4. **Flow-matching head.** AlphaFlow-style flow matching was considered but
   not adopted at M0-M2. Its keep/drop decision is deferred to M4 bench
   results, not architectural argument.

## Release boundaries

Public release operations beyond the M2 GitHub push are not autopilot:

- **M3 PyPI upload** requires a PyPI account + scoped API token.
- **M4 Hugging Face Hub** requires an HF account + write token.
- **M7 arXiv preprint** requires arXiv endorsement + human-form submission.

See `scripts/release.sh` and `INSTRUCTIONS_MANUAL.md` at repository root for
which parts are scripted vs. which remain operator steps.
