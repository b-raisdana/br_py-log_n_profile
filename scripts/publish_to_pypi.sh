#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Load .env
if [[ -f "${REPO_ROOT}/.env" ]]; then
    set -a
    source "${REPO_ROOT}/.env"
    set +a
else
    echo "ERROR: .env file not found at ${REPO_ROOT}/.env"
    exit 1
fi

if [[ -z "${PYPI_API_KEY:-}" ]]; then
    echo "ERROR: PYPI_API_KEY is not set in .env"
    exit 1
fi

cd "${REPO_ROOT}"

# Parse current version from pyproject.toml
CURRENT_VERSION=$(grep -E '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
if [[ -z "${CURRENT_VERSION}" ]]; then
    echo "ERROR: Could not parse current version from pyproject.toml"
    exit 1
fi

# Bump version (default: patch)
BUMP_TYPE="${1:-patch}"
MAJOR=$(echo "${CURRENT_VERSION}" | cut -d. -f1)
MINOR=$(echo "${CURRENT_VERSION}" | cut -d. -f2)
PATCH=$(echo "${CURRENT_VERSION}" | cut -d. -f3)

case "${BUMP_TYPE}" in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
    *)
        echo "ERROR: Invalid bump type '${BUMP_TYPE}'. Use: major, minor, or patch"
        exit 1
        ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
echo "Bumping version: ${CURRENT_VERSION} -> ${NEW_VERSION}"

# Update pyproject.toml
sed -i "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" pyproject.toml

# Update CHANGELOG.md
TODAY=$(date +%Y-%m-%d)
if ! grep -q "## \[${NEW_VERSION}\]" CHANGELOG.md; then
    sed -i "s/^# Changelog$/# Changelog\n\n## [${NEW_VERSION}] - ${TODAY}\n\n### Added\n\n- \n\n### Changed\n\n- \n\n### Fixed\n\n- /" CHANGELOG.md
fi

# Run pre-commit checks (skip main-branch block for release automation)
echo "Running pre-commit checks..."
export SKIP_NO_COMMIT_TO_MAIN=1
PRE_COMMIT_OUTPUT=$(pre-commit run --all-files 2>&1) || true
echo "${PRE_COMMIT_OUTPUT}"

# Auto-stage any fixes from pre-commit
if echo "${PRE_COMMIT_OUTPUT}" | grep -q "files were modified by this hook"; then
    echo "Staging pre-commit auto-fixes..."
    git add -A
fi

# Check if pre-commit passed (excluding no-commit-to-main which we skip)
if echo "${PRE_COMMIT_OUTPUT}" | grep -E "^(ruff|pytest|incremental ratchet).*Failed" > /dev/null; then
    echo "ERROR: Pre-commit checks failed. Fix issues and retry."
    exit 1
fi

# Build package
echo "Building package..."
python -m build

# Publish to PyPI
echo "Publishing to PyPI..."
python -m twine upload dist/* -u "__token__" -p "${PYPI_API_KEY}"

# Commit and push
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v${NEW_VERSION}"
git push origin main

echo "Successfully published version ${NEW_VERSION} to PyPI"
echo "View at: https://pypi.org/project/br-logging-and-profiling/${NEW_VERSION}/"
