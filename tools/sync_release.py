#!/usr/bin/env python3
"""Synchronize checked-in/runtime manifest metadata from config/release.json."""
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "config" / "release.json"
MANIFEST = ROOT / "manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    release = load(RELEASE)
    manifest = load(MANIFEST)

    version = release["version"]
    if not (isinstance(version, list) and len(version) == 3 and all(isinstance(x, int) and x >= 0 for x in version)):
        raise SystemExit("config/release.json: version must be three non-negative integers")
    if release.get("version_string") != ".".join(map(str, version)):
        raise SystemExit("config/release.json: version_string does not match version")

    header = manifest.setdefault("header", {})
    header["name"] = release["name"]
    header["description"] = release["description"]
    header["version"] = version
    header["min_engine_version"] = release["min_engine_version"]

    modules = manifest.get("modules", [])
    if not modules:
        raise SystemExit("manifest.json: at least one module is required")
    for module in modules:
        module["version"] = version

    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Release metadata synchronized: {release['name']} {release['version_string']} (Bedrock {release['target_bedrock']})")


if __name__ == "__main__":
    main()
