#!/usr/bin/env python3
"""Create a deterministic DLavie Visual mcpack from generated runtime files."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "DLavie-Visual.mcpack"
EXCLUDE_TOP = {
    "dist", ".git", "__pycache__", "docs", "THIRD_PARTY_LICENSES", "branding",
    "tools", ".github", "config", "third_party_runtime",
}
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def add_bytes(zf: ZipFile, arcname: str, data: bytes) -> None:
    info = ZipInfo(arcname, FIXED_TIME)
    info.compress_type = ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    zf.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()

    runtime = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] in EXCLUDE_TOP:
            continue
        if rel.name in {".DS_Store", ".gitignore"}:
            continue
        runtime.append((rel.as_posix(), path))

    license_path = ROOT / "THIRD_PARTY_LICENSES" / "DERCODE-License-2.5.txt"
    if not license_path.is_file():
        raise SystemExit("missing THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt")

    arcnames = [name for name, _ in runtime] + ["THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt"]
    if len(arcnames) != len(set(arcnames)):
        raise SystemExit("duplicate archive path detected before packaging")

    with ZipFile(OUT, "w") as zf:
        for arcname, path in runtime:
            add_bytes(zf, arcname, path.read_bytes())
        add_bytes(zf, "THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt", license_path.read_bytes())

    print(f"Built deterministic {OUT} with {len(arcnames)} entries")


if __name__ == "__main__":
    main()
