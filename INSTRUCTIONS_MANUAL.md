# ParaFold — Manual Operator Steps

`scripts/release.sh` handles every step that can be scripted once credentials
are in the environment. This file lists the steps that are **inherently
manual** — account creation, web forms, human identity, wet-lab decisions,
GPU launch — together with the exact URL or command and a wall-clock
estimate.

If a step appears here, it is not because the tooling could not script it; it
is because the gating action is not a Claude-accessible API call.

---

## ONE-TIME ENVIRONMENT (≈10 min)

```bash
# Python ≥3.11
python3 --version

# Recommended: uv (fast installer, optional)
curl -Lsf https://astral.sh/uv/install.sh | sh

# git identity
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"

# gh CLI (used by scripts/release.sh gh-release)
gh auth status   # or: gh auth login
```

---

## M3 — first PyPI release

| # | Step | URL / Command | Effort | Scripted after? |
|---|------|--------------|--------|-----------------|
| 1 | Create a PyPI account | https://pypi.org/account/register/ | 10 min | n/a (one-off) |
| 2 | Generate a scoped API token | https://pypi.org/manage/account/token/ — scope `parafold` | 2 min | n/a |
| 3 | Export the token, then upload | `TWINE_PASSWORD=pypi-... scripts/release.sh pypi` | 1 min | ✅ — all future uploads are scripted |
| 4 | Verify | https://pypi.org/project/parafold/ | 1 min | ✅ |

---

## M4 — Hugging Face Hub weights

| # | Step | URL / Command | Effort | Scripted after? |
|---|------|--------------|--------|-----------------|
| 1 | Create an HF account | https://huggingface.co/join | 5 min | n/a |
| 2 | Generate a write token | https://huggingface.co/settings/tokens | 2 min | n/a |
| 3 | Create the model repo | https://huggingface.co/new (visibility = public, license = MIT) | 2 min | n/a |
| 4 | Upload weights | `HF_TOKEN=hf_... PARAFOLD_WEIGHTS_DIR=./weights scripts/release.sh hf-hub <user>/parafold` | 5 min | ✅ |
| 5 | (Optional) email IEDB about dataset terms | help@iedb.org — ask explicit redistribution permission | 15 min + reply latency | ✗ (legal) |

GPU fine-tune itself runs locally on user hardware:

```bash
# user-supervised, not in scope for release.sh
parafold finetune --config configs/m4_finetune.yaml
```

Wall-clock: 4–24 h per run depending on dataset size; A100 40 GB recommended.

---

## M5 — viz site deploy

| # | Step | URL / Command | Effort | Scripted after? |
|---|------|--------------|--------|-----------------|
| 1 | In repo settings, enable Pages | https://github.com/hinanohart/parafold/settings/pages — Source = "Deploy from a branch" — Branch = `gh-pages` | 2 min | n/a (one-off toggle) |
| 2 | Deploy | `scripts/release.sh docs` | 1 min | ✅ |

`mkdocs.yml` does not yet exist in repo. It lands in M6 (docs phase); until
then `scripts/release.sh docs` exits with an error.

---

## M7 — preprint and journal

| # | Step | URL / Command | Effort | Scripted? |
|---|------|--------------|--------|-----------|
| 1 | Create an arXiv account (if first time) | https://arxiv.org/user/register | 10 min | ✗ |
| 2 | Request endorsement (if first q-bio submission) | https://arxiv.org/auth/show-endorsers/q-bio.BM | up to days | ✗ |
| 3 | Submit preprint | https://arxiv.org/submit — categories `cs.LG` + `q-bio.BM` | 45–90 min | ✗ (form-gated) |
| 4 | Journal submission (Bioinformatics) | https://academic.oup.com/bioinformatics/pages/submission_online | 2–4 h | ✗ |

ORCID is required for the journal submission: https://orcid.org/register

---

## Research decisions that are not automation problems

The architecture memory records six open uncertainties (`docs/index.md > Open
questions (pre-M3)`). Three of them are resolved by **running code** (Claude
can write that code) and three are resolved by **deciding**:

| # | Question | Resolved by |
|---|----------|-------------|
| 1 | Boltz-2 multi-chain API in current release | `python -c "import boltz; help(boltz)"` + read release notes |
| 2 | IEDB / VDJdb redistribution terms | email reply from each provider (legal) |
| 3 | Fine-tune compute envelope | a 100-step dry-run on real hardware (profile) |
| 4 | Niche differentiation vs TCRdock / TCRmodel2 / ImmuneFold | read the papers, decide if margin is novel |
| 5 | README Egan narrative length | M6 (docs phase) review |
| 6 | Flow-matching head | M4 bench results — keep or drop based on RMSD delta |

---

## Quick reference — what gets bundled into the next release

After tokens are in the environment, the entire release flow is:

```bash
# Bump version in pyproject.toml + CITATION.cff
git commit -am "release X.Y.Z"
git tag -a vX.Y.Z -m "ParaFold X.Y.Z"
git push origin main --tags

# Build + GitHub Release + PyPI in one shot
TWINE_PASSWORD=pypi-... scripts/release.sh all
```

That single chain is the entirety of the scripted release path; everything in
the tables above runs once per account.
