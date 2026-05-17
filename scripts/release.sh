#!/usr/bin/env bash
# release.sh — bundle every scripted step of a ParaFold release into one entry-point.
#
# The companion file INSTRUCTIONS_MANUAL.md (at repo root) lists the steps
# that are NOT scripted and must remain operator actions (account creation,
# arXiv form, IEDB licence email, GitHub Pages toggle, GPU launch).
#
# Invocation:
#   scripts/release.sh build              # build sdist + wheel locally
#   scripts/release.sh pypi               # build + upload to PyPI (needs TWINE_PASSWORD)
#   scripts/release.sh gh-release         # build + create GitHub Release with assets
#   scripts/release.sh hf-hub <repo-id>   # upload weights folder to HF Hub (needs HF_TOKEN)
#   scripts/release.sh docs               # build + deploy mkdocs site to gh-pages
#   scripts/release.sh all                # build (once) → gh-release → pypi (skip hf/docs)
#
# Environment variables consumed:
#   TWINE_USERNAME   defaults to "__token__"
#   TWINE_PASSWORD   PyPI scoped API token (required for `pypi` and `all`)
#   HF_TOKEN         Hugging Face write token (required for `hf-hub`; never
#                    appears in argv — exported as HUGGING_FACE_HUB_TOKEN)
#   PARAFOLD_WEIGHTS_DIR  path to local weights folder uploaded by `hf-hub`
#
# Idempotency contract:
#   - `build` always recomputes dist/* from a clean working tree.
#   - `gh-release` reuses existing dist/ (no second build) and re-writes the
#     release title + notes on every invocation.
#   - `pypi` reuses existing dist/ (no second build).
#   - `all` builds exactly once; the bytes uploaded to GitHub Release and
#     PyPI are byte-identical.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Resolve a usable Python interpreter once.
#
# Priority order:
#   1. PYTHON_BIN env override (operator explicitly chose one).
#   2. The repository-local .venv/ (the install path CONTRIBUTING.md asks
#      contributors to create).
#   3. An already-activated VIRTUAL_ENV.
#   4. system `python`.
#   5. system `python3` (Debian/Ubuntu's default name).
#
# Modern Linux distributions enforce PEP 668 on system Python, so the
# release tooling will not be able to `pip install build/twine/...` outside
# a venv. We refuse to run unless we resolved a non-system interpreter,
# rather than fail mid-build with an "externally-managed-environment"
# error.
if [ -n "${PYTHON_BIN:-}" ]; then
    :  # honour explicit override
elif [ -x "$REPO_ROOT/.venv/bin/python" ]; then
    PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    printf 'release.sh: no Python interpreter found\n' >&2
    exit 1
fi

# If we ended up on a system python (no .venv detected), warn loudly.
# PEP 668 will reject `pip install` against /usr/bin/python on modern
# distros; tell the operator to create the venv per CONTRIBUTING.md.
if ! "$PYTHON_BIN" -c 'import sys; sys.exit(0 if sys.prefix != sys.base_prefix else 1)' 2>/dev/null; then
    printf 'release.sh: Python at %s is the system interpreter.\n' "$PYTHON_BIN" >&2
    printf '            PEP 668 may reject pip install. Activate the project venv first:\n' >&2
    printf '              python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"\n' >&2
    printf '            Then re-run scripts/release.sh, or pass PYTHON_BIN=/path/to/venv/python.\n' >&2
    exit 1
fi

# Internal: set to 1 by build() / ensure_dist() so callers downstream can
# skip rebuilding when dist/ is already populated for the current version.
_DIST_READY=0

die() {
    printf 'release.sh: %s\n' "$*" >&2
    exit 1
}

require_clean_tree() {
    if ! git diff --quiet HEAD; then
        die "working tree has uncommitted changes — commit or stash first"
    fi
    if [ -n "$(git ls-files --others --exclude-standard)" ]; then
        die "working tree has untracked files — commit, stash, or .gitignore them first"
    fi
}

current_version() {
    "$PYTHON_BIN" -c 'import tomllib, pathlib; print(tomllib.loads(pathlib.Path("pyproject.toml").read_text())["project"]["version"])'
}

require_tag_at_head() {
    local version
    version="v$(current_version)"
    if ! git tag --points-at HEAD | grep -qx "$version"; then
        die "current HEAD is not tagged '$version' — run \`git tag -a $version -m \"...\" && git push origin $version\` first"
    fi
}

dist_for_version() {
    local version
    version="$(current_version)"
    test -f "dist/parafold-${version}-py3-none-any.whl" \
        && test -f "dist/parafold-${version}.tar.gz"
}

cmd_build() {
    require_clean_tree
    rm -rf dist build ./*.egg-info
    "$PYTHON_BIN" -m pip install --upgrade --quiet build
    "$PYTHON_BIN" -m build
    ls -la dist/
    _DIST_READY=1
}

ensure_dist() {
    if [ "$_DIST_READY" = "1" ] && dist_for_version; then
        return 0
    fi
    if dist_for_version; then
        printf 'release.sh: reusing existing dist/ for v%s\n' "$(current_version)" >&2
        _DIST_READY=1
        return 0
    fi
    cmd_build
}

cmd_pypi() {
    [ -n "${TWINE_PASSWORD:-}" ] \
        || die "TWINE_PASSWORD is required to upload to PyPI (scoped token)"
    ensure_dist
    "$PYTHON_BIN" -m pip install --upgrade --quiet twine
    TWINE_USERNAME="${TWINE_USERNAME:-__token__}" \
        "$PYTHON_BIN" -m twine upload --non-interactive dist/*
}

cmd_gh_release() {
    command -v gh >/dev/null || die "gh CLI not installed"
    require_tag_at_head
    ensure_dist
    local version
    version="v$(current_version)"
    # Refresh title + notes on every invocation so the release page stays in
    # sync with CHANGELOG.md. We extract the matching version section from
    # CHANGELOG.md (between this version's heading and the next).
    # The notes file is cleaned up unconditionally at function exit; we do
    # NOT use `trap ... EXIT` because trap survives the function scope and
    # would fire after `local notes_file` has gone out of scope, tripping
    # `set -u` on an unbound variable.
    local notes_file="${TMPDIR:-/tmp}/parafold-release-notes.$$"
    "$PYTHON_BIN" - <<'PY' "$version" >"$notes_file"
import pathlib
import re
import sys

version_tag = sys.argv[1].lstrip("v")
text = pathlib.Path("CHANGELOG.md").read_text()
pattern = rf"^## \[{re.escape(version_tag)}\][^\n]*\n(?P<body>.*?)(?=^## \[|\Z)"
match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
if match is None:
    sys.stdout.write(f"See CHANGELOG.md for the full diff of {version_tag}.\n")
else:
    sys.stdout.write(match.group("body").rstrip() + "\n")
PY
    if gh release view "$version" >/dev/null 2>&1; then
        gh release edit "$version" \
            --title "ParaFold $version" \
            --notes-file "$notes_file"
        gh release upload "$version" dist/* --clobber
    else
        gh release create "$version" \
            --title "ParaFold $version" \
            --notes-file "$notes_file" \
            dist/*
    fi
    rm -f "$notes_file"
}

cmd_hf_hub() {
    local repo_id="${1:-}"
    [ -n "$repo_id" ] || die "usage: release.sh hf-hub <hf-repo-id>"
    [ -n "${HF_TOKEN:-}" ] \
        || die "HF_TOKEN is required to upload to Hugging Face Hub"
    local weights_dir="${PARAFOLD_WEIGHTS_DIR:-./weights}"
    [ -d "$weights_dir" ] || die "weights directory $weights_dir does not exist"

    "$PYTHON_BIN" -m pip install --upgrade --quiet "huggingface_hub[cli]"
    # Export through HUGGING_FACE_HUB_TOKEN so the token does NOT appear in
    # argv (visible to `ps aux` on multi-tenant hosts). The CLI honours this
    # env var since huggingface_hub 0.20.
    HUGGING_FACE_HUB_TOKEN="$HF_TOKEN" \
        huggingface-cli upload "$repo_id" "$weights_dir" --repo-type model
}

cmd_docs() {
    if [ ! -f mkdocs.yml ]; then
        die "mkdocs.yml not present — docs deploy is M6 scope"
    fi
    "$PYTHON_BIN" -m pip install --upgrade --quiet "mkdocs-material" "mkdocstrings[python]"
    mkdocs gh-deploy --force --clean --verbose
}

cmd_all() {
    # Fail fast on missing credentials BEFORE doing any work.
    [ -n "${TWINE_PASSWORD:-}" ] \
        || die "TWINE_PASSWORD is required for \`release.sh all\` (PyPI step)"
    command -v gh >/dev/null || die "gh CLI not installed (\`release.sh all\` needs it)"
    require_tag_at_head
    cmd_build
    cmd_gh_release
    cmd_pypi
}

main() {
    local subcmd="${1:-}"
    shift || true
    case "$subcmd" in
        build)      cmd_build ;;
        pypi)       cmd_pypi ;;
        gh-release) cmd_gh_release ;;
        hf-hub)     cmd_hf_hub "$@" ;;
        docs)       cmd_docs ;;
        all)        cmd_all ;;
        ""|-h|--help)
            sed -n '2,/^set -e/p' "$0" | head -n 35
            ;;
        *) die "unknown sub-command: $subcmd" ;;
    esac
}

main "$@"
