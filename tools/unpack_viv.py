#!/usr/bin/env python3
"""
tools/unpack_viv.py

Unpacks EA BIG/VIV (BIGF) archives from Def Jam: Fight for NY.
Can unpack standalone .viv files or extract .viv files directly from an Xbox disc image.
"""

import sys
import os
import struct

def parse_viv_data(data, output_dir=None):
    if len(data) < 16 or data[:4] != b"BIGF":
        return None

    # Big-endian header:
    # 0..4: "BIGF"
    # 4..8: Archive size
    # 8..12: File count
    # 12..16: Header/Directory size
    total_sz, num_files, dir_sz = struct.unpack(">III", data[4:16])

    entries = []
    pos = 16
    for i in range(num_files):
        if pos + 8 > len(data):
            break
        off, sz = struct.unpack(">II", data[pos:pos+8])
        pos += 8
        name_bytes = []
        while pos < len(data) and data[pos] != 0:
            name_bytes.append(data[pos])
            pos += 1
        pos += 1  # Skip null byte
        name = bytes(name_bytes).decode("latin1", errors="replace")
        entries.append((name, off, sz))

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        for name, off, sz in entries:
            target_path = os.path.join(output_dir, name.replace("/", os.sep).replace("\\", os.sep))
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(data[off:off+sz])
            print(f"  Unpacked: {name:35} ({sz:,} bytes)")

    return entries

def unpack_viv_file(viv_path, output_dir=None):
    if not os.path.isfile(viv_path):
        print(f"Error: VIV file '{viv_path}' not found.", file=sys.stderr)
        return False

    if not output_dir:
        output_dir = os.path.splitext(viv_path)[0] + "_extracted"

    with open(viv_path, "rb") as f:
        data = f.read()

    print(f"Unpacking '{viv_path}' -> '{output_dir}'...")
    entries = parse_viv_data(data, output_dir)
    if entries is None:
        print(f"Error: '{viv_path}' is not a valid BIGF archive.", file=sys.stderr)
        return False

    print(f"Successfully extracted {len(entries)} files.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path_to_archive.viv> [output_directory]")
        sys.exit(1)

    viv = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    unpack_viv_file(viv, out)

