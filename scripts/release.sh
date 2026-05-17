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
#   scripts/release.sh all                # build → gh-release → pypi (skip hf/docs)
#
# Environment variables consumed:
#   TWINE_USERNAME   defaults to "__token__"
#   TWINE_PASSWORD   PyPI scoped API token (no default; required for `pypi`)
#   HF_TOKEN         Hugging Face write token (required for `hf-hub`)
#   PARAFOLD_WEIGHTS_DIR  path to local weights folder uploaded by `hf-hub`
#
# All commands are idempotent and exit non-zero on the first failure.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

die() {
    printf 'release.sh: %s\n' "$*" >&2
    exit 1
}

require_clean_tree() {
    if ! git diff --quiet HEAD; then
        die "working tree has uncommitted changes — commit or stash first"
    fi
}

current_version() {
    python -c "import tomllib, pathlib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']['version'])"
}

cmd_build() {
    require_clean_tree
    rm -rf dist build ./*.egg-info
    python -m pip install --upgrade --quiet build
    python -m build
    ls -la dist/
}

cmd_pypi() {
    cmd_build
    if [ -z "${TWINE_PASSWORD:-}" ]; then
        die "TWINE_PASSWORD is required to upload to PyPI (scoped token)"
    fi
    python -m pip install --upgrade --quiet twine
    TWINE_USERNAME="${TWINE_USERNAME:-__token__}" \
        python -m twine upload --non-interactive dist/*
}

cmd_gh_release() {
    command -v gh >/dev/null || die "gh CLI not installed"
    cmd_build
    local version
    version="v$(current_version)"
    if gh release view "$version" >/dev/null 2>&1; then
        gh release upload "$version" dist/* --clobber
    else
        gh release create "$version" \
            --title "ParaFold $version" \
            --notes-file <(printf 'See CHANGELOG and commit log for changes.\n') \
            dist/*
    fi
}

cmd_hf_hub() {
    local repo_id="${1:-}"
    [ -n "$repo_id" ] || die "usage: release.sh hf-hub <hf-repo-id>"
    [ -n "${HF_TOKEN:-}" ] || die "HF_TOKEN is required to upload to Hugging Face Hub"
    local weights_dir="${PARAFOLD_WEIGHTS_DIR:-./weights}"
    [ -d "$weights_dir" ] || die "weights directory $weights_dir does not exist"

    python -m pip install --upgrade --quiet "huggingface_hub[cli]"
    huggingface-cli upload "$repo_id" "$weights_dir" --token "$HF_TOKEN" --repo-type model
}

cmd_docs() {
    python -m pip install --upgrade --quiet "mkdocs-material" "mkdocstrings[python]"
    if [ ! -f mkdocs.yml ]; then
        die "mkdocs.yml not present — docs deploy is M6 scope"
    fi
    mkdocs gh-deploy --force --clean --verbose
}

cmd_all() {
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
            sed -n '2,/^set -e/p' "$0" | head -n 25
            ;;
        *) die "unknown sub-command: $subcmd" ;;
    esac
}

main "$@"
