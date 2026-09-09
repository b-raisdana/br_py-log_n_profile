#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec python publish_to_pypi.py "$@"
