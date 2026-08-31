#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/generate_assets.py
python3 tools/validate_pack.py
rm -rf dist
mkdir -p dist
zip -q -r dist/DLavie-Visual.mcpack manifest.json pack_icon.png LICENSE texts subpacks \
  -x '*/.DS_Store'
printf 'Built dist/DLavie-Visual.mcpack\n'
