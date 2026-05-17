#!/usr/bin/env bash
# manual_steps.sh — interactive wizard for every step that release.sh cannot script.
#
# Run from anywhere:   bash scripts/manual_steps.sh [--non-interactive]
#
# This wizard walks through the seven inherently-manual gates listed in
# INSTRUCTIONS_MANUAL.md. For each gate it:
#   1. detects whether the gate is already passed (env var present, gh setting on,
#      remote release published, etc.) and prints a check;
#   2. for steps that CAN be automated (e.g. enabling GitHub Pages once the
#      gh-pages branch exists, running scripts/release.sh once tokens are set)
#      it runs them inline;
#   3. for steps that CANNOT (web form, identity, wet-lab decision, email reply)
#      it prints the exact URL and pauses until you press enter.
#
# Secrets are NEVER echoed. Tokens are accepted as env vars only; if you must
# paste them, the wizard reads with `read -s` so the value never enters the
# terminal log.

set -euo pipefail

NONINTERACTIVE=0
if [[ "${1:-}" == "--non-interactive" ]]; then NONINTERACTIVE=1; fi

# ---- helpers -----------------------------------------------------------------

c_green() { printf '\033[32m%s\033[0m' "$1"; }
c_yellow() { printf '\033[33m%s\033[0m' "$1"; }
c_red() { printf '\033[31m%s\033[0m' "$1"; }
c_cyan() { printf '\033[36m%s\033[0m' "$1"; }

step() {
  local n="$1"; shift
  printf '\n%s %s\n' "$(c_cyan "[$n]")" "$*"
}
done_mark() { printf '   %s\n' "$(c_green '✅ already done')"; }
todo_mark() { printf '   %s %s\n' "$(c_yellow '⏳ manual')" "$1"; }
fail_mark() { printf '   %s %s\n' "$(c_red '✗')" "$1"; }

pause() {
  if [[ $NONINTERACTIVE -eq 1 ]]; then return 0; fi
  printf '   press enter when done, or ctrl-c to abort: '
  read -r _
}

ask_secret() {
  local name="$1" prompt="$2"
  if [[ -n "${!name:-}" ]]; then
    printf '   %s already set in env — keeping it\n' "$name"
    return 0
  fi
  if [[ $NONINTERACTIVE -eq 1 ]]; then
    fail_mark "$name not in env (and --non-interactive given)"
    return 1
  fi
  printf '   %s' "$prompt"
  local value
  read -rs value
  echo
  export "$name=$value"
}

require_repo() {
  if [[ ! -f pyproject.toml ]] || ! grep -q '^name = "parafold"' pyproject.toml; then
    fail_mark "must run from parafold repo root"
    exit 1
  fi
}

# ---- preamble ----------------------------------------------------------------

require_repo

cat <<'BANNER'
================================================================================
ParaFold release wizard — every manual gate, one script.
   scripted parts: scripts/release.sh
   web gates:      walked through below
================================================================================
BANNER

# ---- ENV 0 -------------------------------------------------------------------

step 0 "one-time environment"

if command -v python3 >/dev/null && python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'; then
  done_mark
else
  todo_mark "python ≥3.11 not found — install python3.11 / 3.12 first"; pause
fi

if [[ -d .venv ]]; then
  done_mark
else
  todo_mark "creating project venv (.venv)"
  python3 -m venv .venv
  .venv/bin/pip install -U pip
  .venv/bin/pip install -e '.[dev]'
fi

if gh auth status >/dev/null 2>&1; then
  done_mark
else
  todo_mark "gh CLI not authenticated — run: gh auth login"; pause
fi

# ---- GATE 1: PyPI (M3) -------------------------------------------------------

step 1 "M3 — PyPI account + API token"

if [[ -n "${TWINE_PASSWORD:-}" ]]; then
  done_mark
else
  todo_mark "open https://pypi.org/account/register/  (10 min, one-off)"; pause
  todo_mark "open https://pypi.org/manage/account/token/  (scope = parafold, 2 min)"
  ask_secret TWINE_PASSWORD "paste your pypi-AgEI... token (silent): "
fi

# ---- GATE 2: Hugging Face (M4) -----------------------------------------------

step 2 "M4 — Hugging Face write token (skip if not at M4 yet)"

if [[ -n "${HF_TOKEN:-}" ]]; then
  done_mark
elif [[ $NONINTERACTIVE -eq 1 ]]; then
  todo_mark "HF_TOKEN not set — skipping (set when M4 lands)"
else
  printf '   skip for now? [Y/n] '
  read -r ans
  if [[ "$ans" =~ ^([Nn])$ ]]; then
    todo_mark "open https://huggingface.co/join then https://huggingface.co/settings/tokens"; pause
    ask_secret HF_TOKEN "paste your hf_... write token (silent): "
  else
    todo_mark "skipped — re-run wizard at M4"
  fi
fi

# ---- GATE 3: IEDB / VDJdb redistribution email -------------------------------

step 3 "M4 — IEDB / VDJdb redistribution permission email (legal, async)"

if [[ -f .iedb_clearance ]]; then
  done_mark
else
  todo_mark "email help@iedb.org and the VDJdb maintainers, ask explicit re-distribution permission"
  todo_mark "when their reply lands, touch .iedb_clearance and commit it"
  printf '   skip until reply? [Y/n] '
  if [[ $NONINTERACTIVE -eq 0 ]]; then read -r _; fi
fi

# ---- GATE 4: GitHub Pages toggle (auto when gh-pages branch exists) ---------

step 4 "M5 — GitHub Pages source = gh-pages branch"

pages_state=$(gh api repos/hinanohart/parafold/pages 2>/dev/null | grep -o '"status":"[^"]*"' | head -1 || true)
if [[ -n "$pages_state" ]]; then
  done_mark
else
  if git ls-remote --exit-code origin gh-pages >/dev/null 2>&1; then
    todo_mark "gh-pages branch exists — enabling Pages via gh api"
    gh api -X POST repos/hinanohart/parafold/pages \
      -F 'source[branch]=gh-pages' -F 'source[path]=/' \
      && done_mark \
      || todo_mark "auto-enable failed — toggle manually at https://github.com/hinanohart/parafold/settings/pages"
  else
    todo_mark "gh-pages branch does not exist yet (lands in M6) — toggle manually later at https://github.com/hinanohart/parafold/settings/pages"
  fi
fi

# ---- GATE 5: arXiv account + endorsement -------------------------------------

step 5 "M3 (timing) / M7 (scope) — arXiv account, endorsement, preprint"

if [[ -f .arxiv_submitted ]]; then
  done_mark
else
  todo_mark "if first time: https://arxiv.org/user/register  (10 min)"
  todo_mark "if first q-bio submission: https://arxiv.org/auth/show-endorsers/q-bio.BM  (up to days)"
  todo_mark "submit cs.LG + q-bio.BM concurrently with M3 PyPI cut: https://arxiv.org/submit  (45-90 min)"
  todo_mark "when submitted, touch .arxiv_submitted"
  printf '   skip for now? [Y/n] '
  if [[ $NONINTERACTIVE -eq 0 ]]; then read -r _; fi
fi

# ---- GATE 6: ORCID + Bioinformatics journal (M7 only) -----------------------

step 6 "M7 — Bioinformatics journal submission (after benchmark results)"

if [[ -f .journal_submitted ]]; then
  done_mark
else
  todo_mark "ORCID (required): https://orcid.org/register"
  todo_mark "Bioinformatics portal: https://academic.oup.com/bioinformatics/pages/submission_online  (2-4 h)"
  todo_mark "this is M7-gated; skip during M3/M4/M5"
fi

# ---- GATE 7: GPU fine-tune launch (M4 train) ---------------------------------

step 7 "M4 — GPU fine-tune (user hardware / cloud rental)"

if command -v nvidia-smi >/dev/null && nvidia-smi -L 2>/dev/null | grep -q GPU; then
  printf '   %s nvidia GPU detected: %s\n' "$(c_green 'ℹ')" "$(nvidia-smi -L | head -1)"
else
  printf '   %s no nvidia GPU on this host — rent A100 (Lambda / Vast.ai / Modal) or run on owned hardware\n' "$(c_yellow 'ℹ')"
fi
todo_mark "command (run from a GPU host): parafold finetune --config configs/m4_finetune.yaml"
todo_mark "wall-clock: 4-24 h, A100 40 GB recommended; not in scope for release.sh"

# ---- SCRIPTED PART -----------------------------------------------------------

step 8 "scripted release (uses tokens collected above)"

if [[ -n "${TWINE_PASSWORD:-}" ]]; then
  printf '   ready to run: TWINE_PASSWORD=*** scripts/release.sh all\n'
  if [[ $NONINTERACTIVE -eq 0 ]]; then
    printf '   run release.sh all now? [y/N] '
    read -r ans
    if [[ "$ans" =~ ^([Yy])$ ]]; then
      scripts/release.sh all
    else
      printf '   skipped — run later with: TWINE_PASSWORD=*** scripts/release.sh all\n'
    fi
  fi
else
  todo_mark "TWINE_PASSWORD not set — release.sh pypi/all will fail"
fi

# ---- FINAL SUMMARY -----------------------------------------------------------

cat <<'EOF'

================================================================================
What still requires a human (and why)
================================================================================
  1. PyPI / HF Hub / arXiv / ORCID account creation
        → identity-gated web forms (email confirm, CAPTCHA). Cannot be automated.
  2. IEDB / VDJdb redistribution permission
        → legal reply from a third party. Cannot be automated.
  3. arXiv endorsement for q-bio.BM (first-time submitters only)
        → human endorser sends letter. Can take days.
  4. GPU fine-tune launch
        → not a credential problem, a hardware/cost problem. Run on your A100.
  5. Bioinformatics journal submission (M7 only)
        → publisher portal requires ORCID, manuscript file, cover letter.

Everything else (build, sdist, wheel, GitHub Release, PyPI upload,
HF Hub upload, mkdocs deploy, GitHub Pages enable if branch exists)
is fully scripted via scripts/release.sh.
================================================================================
EOF
