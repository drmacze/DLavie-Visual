#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Fail early on stale/orphan source systems before generating runtime content.
python3 -B tools/audit_release.py source
python3 -B tools/sync_release.py

# Visual-only build: no block albedo/normal/AO/MERS generation in this project.
# Root renderer folders are regenerated too because 4.5.2 installs a safe Natural-Medium
# fallback there; selected subpacks still override those root files normally.
rm -rf biomes subpacks textures pack_icon.png _quality_subpacks \
  atmospherics lighting color_grading fogs water pbr local_lighting shadows
python3 -B tools/generate_configs.py >/dev/null
echo "Generated base renderer configs"
python3 -B tools/generate_assets.py >/dev/null
echo "Generated visual environment assets"
python3 -B tools/generate_optical_caustics.py
python3 -B tools/generate_themes.py
python3 -B tools/enhance_visual_core.py
python3 -B tools/enhance_volumetric_fog.py
python3 -B tools/enhance_weather_water.py
python3 -B tools/enhance_underwater_night.py
python3 -B tools/enhance_pbr_compat.py

# Feature-level validator + cross-system runtime audit.
python3 -B tools/validate_pack.py
python3 -B tools/audit_release.py generated

rm -rf dist
mkdir -p dist
python3 -B tools/package_mcpack.py
python3 -B tools/audit_release.py mcpack dist/DLavie-Visual.mcpack
