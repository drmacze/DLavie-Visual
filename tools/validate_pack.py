#!/usr/bin/env python3
"""Dependency-free structural validation for the Bedrock resource pack."""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

def fail(message):
    ERRORS.append(message)

try:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
except Exception as exc:
    sys.exit(f"manifest.json is invalid: {exc}")

if manifest.get("format_version") != 2:
    fail("manifest format_version must be 2")
subpacks = manifest.get("subpacks", [])
if [item.get("folder_name") for item in subpacks] != ["low", "medium", "high"]:
    fail("manifest must expose low, medium, and high in that order")

expected = {"low": 32, "medium": 64, "high": 128}
for preset, size in expected.items():
    base = ROOT / "subpacks" / preset / "textures"
    for rel in ("environment/clouds.png", "environment/sun.png",
                "environment/moon_phases.png", "colormap/grass.png",
                "colormap/foliage.png"):
        path = base / rel
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT)}")
            continue
        data = path.read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            fail(f"not a PNG: {path.relative_to(ROOT)}")
            continue
        width, height = struct.unpack(">II", data[16:24])
        wanted = (size * 4, size * 2) if rel == "environment/moon_phases.png" else (size, size)
        if (width, height) != wanted:
            fail(f"{path.relative_to(ROOT)} is {width}x{height}; expected {wanted[0]}x{wanted[1]}")

if ERRORS:
    print("Pack validation failed:")
    print("\n".join(f"- {error}" for error in ERRORS))
    sys.exit(1)
print("Pack validation passed: manifest, presets, and PNG dimensions are valid.")
