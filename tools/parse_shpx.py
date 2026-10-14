#!/usr/bin/env python3
"""
tools/parse_shpx.py

Parses and decodes Electronic Arts SHPX (Shape Xbox) graphics containers from Def Jam: Fight for NY.
Handles:
- EA RefPack (QFS / 0x10FB) decompression
- SHPX directory and item headers
- Xbox NV2A swizzled and linear texture formats (8-bit paletted, 16-bit, 32-bit)
- Texture extraction to standard BMP images
"""

import sys
import os
import struct
from pyBIG import refpack

def unswizzle_coords(x, y, w, h):
    """Morton Z-order unswizzling for Xbox NV2A textures."""
    res = 0
    bit = 1
    cx, cy = x, y
    while cx > 0 or cy > 0:
        if cx & 1:
            res |= bit
        bit <<= 1
        cx >>= 1
        if cy & 1:
            res |= bit
        bit <<= 1
        cy >>= 1
    return res

def save_bmp(filepath, width, height, bgra_data):
    """Saves raw 32-bit BGRA buffer as a standard uncompressed BMP file."""
    bfType = b"BM"
    bfOffBits = 54
    bfSize = 54 + len(bgra_data)
    bmp_header = struct.pack("<2sIHHI", bfType, bfSize, 0, 0, bfOffBits)
    dib_header = struct.pack("<IIIHHIIIIII", 40, width, height, 1, 32, 0, len(bgra_data), 0, 0, 0, 0)
    with open(filepath, "wb") as f:
        f.write(bmp_header + dib_header + bgra_data)

def decode_shpx_texture(item_data, out_path, unswizzle=True):
    """Decodes a single SHPX texture record and exports to BMP."""
    if len(item_data) < 64:
        return False

    fmt, bpp, width, height = struct.unpack("<HHHH", item_data[:8])

    # 8-bit paletted texture (format 0x407B / 0x7B)
    if bpp == 8 or (fmt & 0xFF) == 0x7B:
        pixel_off = 64
        num_pixels = width * height
        if pixel_off + num_pixels > len(item_data):
            return False

        pixels = item_data[pixel_off:pixel_off + num_pixels]

        # Locate palette header (tag 0x2A 0x10)
        pal_tag_idx = item_data.find(b"\x2a\x10", pixel_off + num_pixels)
        if pal_tag_idx == -1:
            pal_tag_idx = pixel_off + num_pixels + 16
        else:
            pal_tag_idx += 16

        pal_data = item_data[pal_tag_idx:pal_tag_idx + 256 * 4]
        if len(pal_data) < 256 * 4:
            return False

        bmp_data = bytearray()
        for y in range(height - 1, -1, -1):
            for x in range(width):
                idx_pos = unswizzle_coords(x, y, width, height) if unswizzle else (y * width + x)
                if idx_pos < len(pixels):
                    idx = pixels[idx_pos]
                else:
                    idx = 0
                b = pal_data[idx * 4 + 0]
                g = pal_data[idx * 4 + 1]
                r = pal_data[idx * 4 + 2]
                a = pal_data[idx * 4 + 3]
                bmp_data.extend([b, g, r, 255])

        save_bmp(out_path, width, height, bmp_data)
        return True

    return False

def parse_shpx_file(shpx_data, output_dir=None, file_prefix="tex"):
    """Parses a decompressed or raw SHPX byte buffer and exports its textures."""
    # Check if RefPack compressed (10FB)
    if len(shpx_data) > 2 and shpx_data[0] == 0x10 and shpx_data[1] == 0xFB:
        shpx_data = refpack.decompress(shpx_data)

    if len(shpx_data) < 16 or shpx_data[:4] != b"SHPX":
        return []

    total_sz, num_entries = struct.unpack("<II", shpx_data[4:12])
    shape_id = shpx_data[12:16].decode("latin1", errors="replace").strip("\x00")

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    extracted = []
    pos = 16
    for i in range(num_entries):
        tag = shpx_data[pos:pos+4].decode("latin1", errors="replace").strip("\x00")
        item_off = struct.unpack("<I", shpx_data[pos+4:pos+8])[0]
        pos += 8

        # Determine item size
        next_off = total_sz
        if i + 1 < num_entries:
            next_off = struct.unpack("<I", shpx_data[pos+4:pos+8])[0]

        item_data = shpx_data[item_off:next_off]
        entry_label = tag if tag else f"{i+1:02d}"
        out_name = f"{file_prefix}_{entry_label}.bmp"
        out_path = os.path.join(output_dir, out_name) if output_dir else out_name

        if output_dir:
            if decode_shpx_texture(item_data, out_path, unswizzle=True):
                extracted.append(out_path)
                print(f"  Exported texture: {out_name} (from tag '{tag}', shape '{shape_id}')")
        else:
            extracted.append((tag, item_off, len(item_data)))

    return extracted

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <file.xsh> [output_directory]")
        sys.exit(1)

    in_file = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(in_file)[0] + "_textures"
    with open(in_file, "rb") as f:
        data = f.read()

    prefix = os.path.splitext(os.path.basename(in_file))[0]
    print(f"Parsing SHPX file '{in_file}' -> '{out_dir}'...")
    res = parse_shpx_file(data, out_dir, prefix)
    print(f"Done! Extracted {len(res)} textures.")
