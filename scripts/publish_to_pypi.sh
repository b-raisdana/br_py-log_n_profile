#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "${CURRENT_BRANCH}" != "main" ]]; then
    echo "ERROR: Must be on 'main' to release. Current branch: ${CURRENT_BRANCH}"
    exit 1
fi

# Load .env
if [[ -f ".env" ]]; then
    set -a
    source ".env"
    set +a
else
    echo "ERROR: .env file not found at ${REPO_ROOT}/.env"
    exit 1
fi

if [[ -z "${PYPI_API_KEY:-}" ]]; then
    echo "ERROR: PYPI_API_KEY is not set in .env"
    exit 1
fi

# Parse current version from pyproject.toml
CURRENT_VERSION=$(grep -E '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
if [[ -z "${CURRENT_VERSION}" ]]; then
    echo "ERROR: Could not parse current version from pyproject.toml"
    exit 1
fi

# Require an explicit release type; accept it as an argument or prompt for it.
BUMP_TYPE="${1:-}"
while [[ -z "${BUMP_TYPE}" ]]; do
    read -r -p "Release type (major/minor/bug fix): " BUMP_TYPE
done

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
    "bug fix" | bugfix | patch)
        PATCH=$((PATCH + 1))
        ;;
    *)
        echo "ERROR: Invalid release type '${BUMP_TYPE}'. Use: major, minor, or bug fix"
        exit 1
        ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
echo "Bumping version: ${CURRENT_VERSION} -> ${NEW_VERSION}"

# Update pyproject.toml
sed -i "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" pyproject.toml

# Generate changelog details from git log between last tag and HEAD
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
CHANGELOG_TMP=$(mktemp)
if [[ -z "${LAST_TAG}" ]]; then
    git log --oneline --graph --decorate > "${CHANGELOG_TMP}"
else
    git log --oneline --graph --decorate "${LAST_TAG}..HEAD" > "${CHANGELOG_TMP}"
fi

TODAY=$(date +%Y-%m-%d)

# Update CHANGELOG.md
python3 - <<PYEOF
import re
import sys

with open('CHANGELOG.md', 'r') as f:
    content = f.read()

with open('${CHANGELOG_TMP}', 'r') as f:
    log_body = f.read()

new_version = "${NEW_VERSION}"
today = "${TODAY}"

new_section = f"## [{new_version}] - {today}\\n\\n### Added\\n\\n- \\n\\n### Changed\\n\\n- \\n\\n### Fixed\\n\\n- \\n\\n{log_body}"

# Remove any existing section for this version
pattern = rf'## \\[{re.escape(new_version)}\\] - .*?(?=\\n## \\[|$)'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Prepend new section after # Changelog
content = content.replace('# Changelog', f'# Changelog\\n\\n{new_section}', 1)

with open('CHANGELOG.md', 'w') as f:
    f.write(content)
PYEOF

rm -f "${CHANGELOG_TMP}"

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

# Create and push tag
TAG_NAME="v${NEW_VERSION}"
echo "Creating tag ${TAG_NAME}..."
git tag "${TAG_NAME}"
git push origin "${TAG_NAME}"

echo "Successfully published version ${NEW_VERSION} to PyPI"
echo "View at: https://pypi.org/project/br-logging-and-profiling/${NEW_VERSION}/"
