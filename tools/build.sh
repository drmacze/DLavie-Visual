#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Visual-only build: no block albedo/normal/AO/MERS generation in this project.
rm -rf biomes subpacks textures pack_icon.png
python3 tools/generate_configs.py
python3 tools/generate_assets.py
python3 tools/generate_optical_caustics.py
python3 tools/generate_themes.py
python3 tools/enhance_visual_core.py
python3 tools/enhance_volumetric_fog.py
python3 tools/enhance_weather_water.py
python3 tools/validate_pack.py
rm -rf dist
mkdir -p dist
python3 - <<'PY2'
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path('.')
out=root/'dist'/'DLavie-Visual.mcpack'
exclude={'dist','.git','__pycache__','docs','THIRD_PARTY_LICENSES','branding','tools','.github','config','third_party_runtime'}
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if rel.parts[0] in exclude: continue
        if rel.name in {'.DS_Store','.gitignore'}: continue
        z.write(p,rel.as_posix())
    z.write(root/'THIRD_PARTY_LICENSES'/'DERCODE-License-2.5.txt','THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt')
print(f'Built {out}')
PY2