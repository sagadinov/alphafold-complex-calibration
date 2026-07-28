#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f MANIFEST.sha256 ]]; then
  echo "MANIFEST.sha256 not found in repository root" >&2
  exit 1
fi

sha256sum -c MANIFEST.sha256
echo "All manifest checks passed."
