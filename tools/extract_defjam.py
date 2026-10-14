#!/usr/bin/env python3
"""
tools/extract_defjam.py

Extracts Def Jam: Fight for NY game data and default.xbe from an original Xbox disc image (.bin / .iso / .xiso).
Based on the XDVDFS parser implementation of OpenCE.
"""

import os
import sys
import struct

SECTOR_SIZE = 2048
VOLUME_MAGIC = b"MICROSOFT*XBOX*MEDIA"
PARTITION_OFFSETS = [0, 0x0FD90000, 0x02080000, 0x18300000]

def extract_image(image_path, output_dir):
    if not os.path.isfile(image_path):
        print(f"Error: Disc image '{image_path}' not found.", file=sys.stderr)
        return False

    os.makedirs(output_dir, exist_ok=True)
    with open(image_path, "rb") as f:
        file_size = os.path.getsize(image_path)
        partition = None
        root_sector = None
        root_size = None

        for offset in PARTITION_OFFSETS:
            vol_offset = offset + 0x10000
            if vol_offset + SECTOR_SIZE <= file_size:
                f.seek(vol_offset)
                sector_data = f.read(SECTOR_SIZE)
                if sector_data[:20] == VOLUME_MAGIC:
                    partition = offset
                    root_sector, root_size = struct.unpack("<II", sector_data[20:28])
                    print(f"Found XDVDFS partition at offset 0x{offset:08X} (root sec {root_sector}, size {root_size} bytes)")
                    break

        if partition is None:
            print("Error: Not a valid Xbox disc image or unrecognized partition layout.", file=sys.stderr)
            return False

        def read_directory(sector, size, current_path=""):
            f.seek(partition + sector * SECTOR_SIZE)
            table = f.read(size)

            def walk_table(offset, depth=0):
                if depth > 64 or offset * 4 + 14 > len(table):
                    return
                entry = table[offset * 4:]
                left, right = struct.unpack("<HH", entry[:4])
                if left == 0xFFFF:
                    return
                if left:
                    walk_table(left, depth + 1)

                sec, sz, attr, name_len = struct.unpack("<IIBB", entry[4:14])
                name = entry[14:14 + name_len].decode("latin1", errors="replace")
                is_dir = bool(attr & 0x10)
                full_path = f"{current_path}/{name}" if current_path else name

                if is_dir:
                    read_directory(sec, sz, full_path)
                else:
                    target_file = os.path.join(output_dir, full_path)
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    pos = f.tell()
                    f.seek(partition + sec * SECTOR_SIZE)
                    data = f.read(sz)
                    with open(target_file, "wb") as out_f:
                        out_f.write(data)
                    f.seek(pos)
                    print(f"Extracted: {full_path} ({sz:,} bytes)")

                if right:
                    walk_table(right, depth + 1)

            walk_table(0)

        print(f"Extracting files into '{output_dir}'...")
        read_directory(root_sector, root_size)
        print("Extraction complete!")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        default_img = os.path.join("Def Jam - Fight for NY", "Xbox - Def Jam Fight for NY.bin")
        default_out = os.path.join("Def Jam - Fight for NY", "extracted")
        if os.path.exists(default_img):
            extract_image(default_img, default_out)
        else:
            print(f"Usage: python {sys.argv[0]} <path_to_xbox_disc.iso/.bin> [output_directory]")
    else:
        img = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else os.path.join("Def Jam - Fight for NY", "extracted")
        extract_image(img, out)

