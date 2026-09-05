# incremental pre-commit ratchet

Two layers: per-touched-file blocking gate and project-wide trend baseline.

Blocking gate: for every touched file, compare its own violation count before vs after this commit. Block only if it regressed.

Trend baseline: `baseline*.json` tracks project-wide counts. Never blocks; used for long-term debt tracking.
