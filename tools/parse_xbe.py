#!/usr/bin/env python3
"""
tools/parse_xbe.py

Inspects and decodes an Xbox executable (default.xbe), extracting section maps,
entry points, statically linked libraries, and kernel import thunks.
"""

import sys
import os
import struct

XBE_DEBUG_EP_KEY = 0x94859D4B
XBE_RETAIL_EP_KEY = 0xA8FC57AB
XBE_DEBUG_THUNK_KEY = 0xEFB1F152
XBE_RETAIL_THUNK_KEY = 0x5B6D40B6

def inspect_xbe(path):
    if not os.path.isfile(path):
        print(f"Error: XBE file '{path}' not found.", file=sys.stderr)
        return

    with open(path, "rb") as f:
        data = f.read()

    if data[:4] != b"XBEH":
        print("Error: Not a valid XBE file (magic mismatch).", file=sys.stderr)
        return

    base_addr = struct.unpack("<I", data[0x104:0x108])[0]
    headers_sz = struct.unpack("<I", data[0x108:0x10C])[0]
    image_sz = struct.unpack("<I", data[0x10C:0x110])[0]
    cert_addr = struct.unpack("<I", data[0x118:0x11C])[0]
    num_sections = struct.unpack("<I", data[0x11C:0x120])[0]
    sections_addr = struct.unpack("<I", data[0x120:0x124])[0]
    entry_point_enc = struct.unpack("<I", data[0x128:0x12C])[0]
    kthunk_enc = struct.unpack("<I", data[0x158:0x15C])[0]
    lib_count = struct.unpack("<I", data[0x160:0x164])[0]
    lib_addr = struct.unpack("<I", data[0x164:0x168])[0]

    ep_debug = entry_point_enc ^ XBE_DEBUG_EP_KEY
    ep_retail = entry_point_enc ^ XBE_RETAIL_EP_KEY
    kthunk_debug = kthunk_enc ^ XBE_DEBUG_THUNK_KEY
    kthunk_retail = kthunk_enc ^ XBE_RETAIL_THUNK_KEY

    print("=== XBE HEADER SUMMARY ===")
    print(f"Base Address:       0x{base_addr:08X}")
    print(f"Headers Size:       {headers_sz:,} bytes")
    print(f"Virtual Image Size: {image_sz:,} bytes ({image_sz / (1024*1024):.2f} MB)")
    print(f"Entry Point:        0x{entry_point_enc:08X} (Debug decoded: 0x{ep_debug:08X}, Retail: 0x{ep_retail:08X})")
    print(f"Kernel Thunk Addr:  0x{kthunk_enc:08X} (Debug decoded: 0x{kthunk_debug:08X}, Retail: 0x{kthunk_retail:08X})")

    if cert_addr >= base_addr:
        coff = cert_addr - base_addr
        cdata = data[coff:coff+464]
        title_id = struct.unpack("<I", cdata[8:12])[0]
        title_name = cdata[12:12+80].decode("utf-16le", errors="replace").rstrip("\x00")
        print(f"Title ID:           0x{title_id:08X}")
        print(f"Title Name:         {title_name}")

    dbg_path_addr = struct.unpack("<I", data[0x14C:0x150])[0]
    if dbg_path_addr >= base_addr:
        dpoff = dbg_path_addr - base_addr
        dbg_path = data[dpoff:dpoff+128].split(b"\x00")[0].decode("latin1", errors="replace")
        print(f"Original Build Path: {dbg_path}")

    print(f"\n=== STATIC XDK LIBRARIES ({lib_count}) ===")
    if lib_addr >= base_addr:
        loff = lib_addr - base_addr
        for i in range(lib_count):
            item = data[loff + i*16 : loff + (i+1)*16]
            name = item[:8].rstrip(b"\x00").decode("latin1", errors="replace")
            major, minor, build, qfe = struct.unpack("<HHHH", item[8:16])
            print(f"  [{i+1}] {name:10} v{major}.{minor}.{build}.{qfe}")

    print(f"\n=== MEMORY SECTIONS ({num_sections}) ===")
    if sections_addr >= base_addr:
        soff = sections_addr - base_addr
        for i in range(num_sections):
            sdata = data[soff + i*56 : soff + (i+1)*56]
            flags, virt_addr, virt_sz, raw_addr, raw_sz, name_addr, name_ref = struct.unpack("<IIIIIII", sdata[:28])
            sname = "?"
            if name_addr >= base_addr:
                noff = name_addr - base_addr
                sname = data[noff:noff+32].split(b"\x00")[0].decode("latin1", errors="replace")
            print(f"  [{i:2d}] {sname:12} Virt: 0x{virt_addr:08X} ({virt_sz:>8,} B) | Raw: 0x{raw_addr:08X} ({raw_sz:>8,} B) | Flags: 0x{flags:08X}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join("Def Jam - Fight for NY", "extracted", "default.xbe")
    inspect_xbe(target)

