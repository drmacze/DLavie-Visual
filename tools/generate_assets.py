#!/usr/bin/env python3
"""Generate all original DLavie Visual PNG assets without third-party packages."""
import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def png(path, width, height, pixel):
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            rows.extend(max(0, min(255, round(v))) for v in pixel(x, y))
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    payload = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    payload += chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)

def noise(x, y, seed):
    value = math.sin(x * 12.9898 + y * 78.233 + seed * 19.19) * 43758.5453
    return value - math.floor(value)

def make_icon():
    n = 512
    def pixel(x, y):
        dx, dy = x - n / 2, y - n / 2
        glow = max(0, 1 - math.hypot(dx, dy) / 350)
        grain = noise(x // 3, y // 3, 7) * 7
        bg = (5 + 8 * glow + grain, 12 + 24 * glow + grain, 25 + 43 * glow + grain, 255)
        # Geometric D: vertical stem and rounded ring, with a cyan-to-gold gradient.
        outer = ((x - 250) / 155) ** 2 + ((y - 256) / 185) ** 2 <= 1 and x >= 170
        inner = ((x - 250) / 82) ** 2 + ((y - 256) / 112) ** 2 <= 1 and x >= 218
        stem = 135 <= x <= 218 and 71 <= y <= 441
        mark = stem or (outer and not inner)
        if mark:
            t = y / n
            return (42 + 220 * t, 221 - 55 * t, 255 - 154 * t, 255)
        return bg
    png(ROOT / "pack_icon.png", n, n, pixel)

def make_preset(name, size, saturation, cloud_alpha):
    base = ROOT / "subpacks" / name / "textures"
    def cloud(x, y):
        u, v = x / size, y / size
        large = (math.sin(u * 13 + math.sin(v * 8)) + math.sin(v * 17) + 2) / 4
        detail = noise(x // max(1, size // 32), y // max(1, size // 32), size)
        density = max(0, min(1, large * .7 + detail * .45 - .44))
        alpha = cloud_alpha * density ** 1.5
        return (235, 244, 255, alpha)
    png(base / "environment/clouds.png", size, size, cloud)

    def sun(x, y):
        d = math.hypot(x - (size - 1) / 2, y - (size - 1) / 2) / (size / 2)
        a = 255 * max(0, min(1, (1.02 - d) * 9))
        return (255, 234 + 15 * (1 - d), 174, a)
    png(base / "environment/sun.png", size, size, sun)

    def moon(x, y):
        phase = (y // size) * 4 + x // size
        lx, ly = x % size, y % size
        d = math.hypot(lx - (size - 1) / 2, ly - (size - 1) / 2) / (size / 2)
        edge = math.cos((phase / 8) * math.tau) * size * .46
        lit = (lx - size / 2 >= edge) if phase < 4 else (lx - size / 2 <= edge)
        a = 255 * max(0, min(1, (1.01 - d) * 12))
        shade = 205 + 34 * noise(lx // 3, ly // 3, 4)
        return (shade, shade + 4, 255, a if lit else a * .2)
    png(base / "environment/moon_phases.png", size * 4, size * 2, moon)

    def grass(x, y):
        heat, rain = x / (size - 1), 1 - y / (size - 1)
        return (45 + 50 * heat, 105 + 75 * rain * saturation, 45 + 45 * rain, 255)
    def foliage(x, y):
        heat, rain = x / (size - 1), 1 - y / (size - 1)
        return (35 + 37 * heat, 91 + 88 * rain * saturation, 39 + 50 * rain, 255)
    png(base / "colormap/grass.png", size, size, grass)
    png(base / "colormap/foliage.png", size, size, foliage)

make_icon()
make_preset("low", 32, .82, 135)
make_preset("medium", 64, 1.0, 175)
make_preset("high", 128, 1.12, 205)
print("Generated original DLavie Visual assets.")
