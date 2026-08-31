#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/generate_configs.py
python3 tools/generate_assets.py
python3 tools/validate_pack.py
rm -rf dist
mkdir -p dist
python3 - <<'PY2'
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path('.')
out=root/'dist'/'DLavie-Visual.mcpack'
exclude={'dist','.git','__pycache__','docs','THIRD_PARTY_LICENSES','branding','tools','.github','config'}
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if rel.parts[0] in exclude: continue
        if rel.name in {'.DS_Store', '.gitignore'}: continue
        z.write(p,rel.as_posix())
    z.write(root/'THIRD_PARTY_LICENSES'/'DERCODE-License-2.5.txt','THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt')
print(f'Built {out}')
PY2
