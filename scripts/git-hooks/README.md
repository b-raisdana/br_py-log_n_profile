# git-hooks

Tracked source of `.git/hooks/pre-commit`. Run `bash scripts/git-hooks/install.sh` once per clone.

`pre-commit` delegates to `precommit_wrapper.py`, which wraps `pre-commit run --hook-stage pre-commit` with failure-snapshotting and logging.
