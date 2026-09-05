#!/bin/sh
set -eu
repo_root="$(git rev-parse --show-toplevel)"
cp "$repo_root/scripts/git-hooks/pre-commit" "$repo_root/.git/hooks/pre-commit"
chmod +x "$repo_root/.git/hooks/pre-commit"
echo "Installed .git/hooks/pre-commit"
