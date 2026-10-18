"""Bounded raw/LZ4/ZBIC NSO decoding, adapted from HY-Leung/nso2elf.

Copyright (c) 2026 NxCheatEngine contributors and HY-Leung.
The adapted code is MIT licensed; see licenses/nso2elf-MIT.txt.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import struct

class ConversionError(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise ConversionError(message)

def unpack(fmt, data, offset=0):
    require(0 <= offset and offset + struct.calcsize(fmt) <= len(data), "Truncated structure")
    return struct.unpack_from(fmt, data, offset)

def u32(data, offset):
    return unpack("<I", data, offset)[0]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def lz4_block(data: bytes, expected: int) -> bytes:
    """Decode the raw LZ4 block used by NSO, including overlapping matches."""
    out = bytearray()
    pos = 0
    def length(base):
        nonlocal pos
        if base == 15:
            while True:
                require(pos < len(data), "Truncated LZ4 length")
                extra = data[pos]
                pos += 1
                base += extra
                require(base <= expected, "LZ4 length exceeds output budget")
                if extra != 255:
                    break
        return base
    while pos < len(data):
        token = data[pos]
        pos += 1
        literals = length(token >> 4)
        require(pos + literals <= len(data), "Truncated LZ4 literals")
        require(len(out) + literals <= expected, "LZ4 output exceeds declared size")
        out.extend(data[pos:pos+literals])
        pos += literals
        if pos == len(data):
            break
        require(pos + 2 <= len(data), "Truncated LZ4 match offset")
        offset = data[pos] | data[pos+1] << 8
        pos += 2
        require(0 < offset <= len(out), "Invalid LZ4 match offset")
        match = length(token & 15) + 4
        require(len(out) + match <= expected, "LZ4 output exceeds declared size")
        # Repeat the existing offset-sized pattern; handles matches longer than offset.
        pattern = out[-offset:]
        if match <= offset:
            out.extend(pattern[:match])
        else:
            out.extend((pattern * ((match + offset - 1) // offset))[:match])
    require(len(out) == expected, "LZ4 decompressed size mismatch")
    return bytes(out)

def zbic_block(data: bytes, expected: int) -> bytes:
    # Validate the frame's advertised allocation BEFORE calling the extension.
    require(data[:4] == b"ZBIC", "Expected ZBIC magic at the declared segment offset")
    require(len(data) >= 5, "Truncated ZBIC frame")
    desc = data[4]
    require(not desc & 0x18, "Unsupported/reserved ZBIC frame bits")
    single = bool(desc & 0x20)
    pos = 5
    if not single:
        require(pos < len(data), "Truncated ZBIC window descriptor")
        window = data[pos]
        pos += 1
        base = 1 << (10 + (window >> 3))
        window_size = base + (base >> 3) * (window & 7)
        require(window_size <= max(expected, 1024), "ZBIC window exceeds segment budget")
    dict_width = (0, 1, 2, 4)[desc & 3]
    require(pos + dict_width <= len(data), "Truncated ZBIC dictionary ID")
    require(int.from_bytes(data[pos:pos+dict_width], "little") == 0,
            "External ZBIC dictionaries are unsupported")
    pos += dict_width
    width = (1 if single else 0, 2, 4, 8)[desc >> 6]
    require(width != 0, "ZBIC frame has no declared content size; bounded decode unavailable")
    require(pos + width <= len(data), "Truncated ZBIC content size")
    size = int.from_bytes(data[pos:pos+width], "little") + (256 if width == 2 else 0)
    require(size == expected, "ZBIC frame content size differs from NSO header")
    try:
        import zbic
    except ImportError as exc:
        raise ConversionError("ZBIC needs: python -m pip install zbic==1.0.1.post1") from exc
    try:
        result = zbic.decompress(data)
    except Exception as exc:
        raise ConversionError(f"ZBIC decompression failed: {exc}") from exc
    require(len(result) == expected, "ZBIC decompressed size mismatch")
    return result

@dataclass
class Segment:
    name: str
    rva: int
    data: bytes
    offset: int
    stored: int
    codec: str
    verified: bool

@dataclass
class Nso:
    header: bytes
    name: bytes
    segments: list[Segment]
    bss: int
    warnings: list[str]
    source_hash: str = ""
    build_notes: list[tuple] | None = None
    relro: tuple[int,int] | None = None

    def region(self, address, size):
        require(address >= 0 and size >= 0, "Negative memory span")
        for segment in self.segments:
            rel = address - segment.rva
            if 0 <= rel and rel + size <= len(segment.data):
                return segment, rel
        raise ConversionError(f"Metadata span 0x{address:x}+0x{size:x} outside initialized segments")

    def read(self, address, size):
        segment, rel = self.region(address, size)
        return segment.data[rel:rel+size]

def parse_nso(raw: bytes, decoded_limit: int) -> Nso:
    require(len(raw) >= 256 and raw[:4] == b"NSO0", "Expected an NSO0 file (NRO/MOD unsupported)")
    require(u32(raw, 4) == 0, "Unsupported NSO version")
    flags = u32(raw, 12)
    require(flags & ~0xff == 0, "Unknown NSO flag bits")
    infos = [unpack("<III", raw, 16+16*i) for i in range(3)]
    require(sum(size for _, _, size in infos) <= decoded_limit, f"Decoded NSO exceeds {decoded_limit}-byte budget")
    spans, segments, warnings = [], [], []
    for i, (off, rva, size) in enumerate(infos):
        compressed = bool(flags & (1 << i))
        stored = u32(raw, 96+4*i) if compressed else size
        require(off >= 256 and off + stored <= len(raw), "NSO segment outside file/header overlap")
        require(all(not (off < end and start < off+stored) for start,end in spans),
                "Overlapping stored NSO segments")
        spans.append((off, off+stored))
        encoded = raw[off:off+stored]
        codec = ("ZBIC" if flags & 0x80 else "LZ4") if compressed else "raw"
        decoded = (zbic_block(encoded, size) if codec == "ZBIC" else
                   lz4_block(encoded, size) if codec == "LZ4" else encoded)
        checked = bool(flags & (1 << (i+3)))
        name = ("text", "rodata", "data")[i]
        if checked:
            require(hashlib.sha256(decoded).digest() == raw[160+32*i:192+32*i],
                    f"{name} SHA-256 mismatch")
        else:
            warnings.append(f"{name}: source hash flag absent, integrity not verified")
        segments.append(Segment(name, rva, decoded, off, stored, codec, checked))
    memory = [(s.rva, s.rva+len(s.data)) for s in segments if s.data]
    bss = u32(raw, 60)
    if bss:
        end = segments[2].rva + len(segments[2].data)
        memory.append((end, end+bss))
    for i,(a,b) in enumerate(memory):
        require(b <= 1 << 32, "NSO memory span exceeds 32-bit RVA space")
        require(all(not (a < d and c < b) for c,d in memory[:i]), "Overlapping NSO memory spans")
    nameoff, namesize = u32(raw, 28), u32(raw, 44)
    name = b""
    if namesize:
        require(namesize <= 1024*1024 and nameoff >= 256 and nameoff+namesize <= len(raw),
                "Invalid NSO module-name span")
        require(all(not (nameoff < end and start < nameoff+namesize) for start,end in spans),
                "NSO module name overlaps segment")
        name = raw[nameoff:nameoff+namesize]
    return Nso(raw[:256], name, segments, bss, warnings, sha(raw))

def uncompressed_nso(nso: Nso) -> bytes:
    out = bytearray(nso.header)
    struct.pack_into("<I", out, 12, u32(out, 12) & ~0x87)
    struct.pack_into("<I", out, 28, 256 if nso.name else 0)
    out.extend(nso.name)
    for i,s in enumerate(nso.segments):
        struct.pack_into("<I", out, 16+16*i, len(out))
        struct.pack_into("<I", out, 96+4*i, len(s.data))
        out.extend(s.data)
    return bytes(out)

MAX_INPUT = 512 * 1024 * 1024
MAX_DECODED = 1024 * 1024 * 1024


def read_nso(path):
    with open(path, "rb") as stream:
        raw = stream.read(MAX_INPUT + 1)
    require(len(raw) <= MAX_INPUT, "NSO input exceeds 512 MiB")
    return raw


def decompress_nso(raw):
    """Return an uncompressed NSO0, retaining RVAs, BSS and Build ID."""
    require(len(raw) <= MAX_INPUT, "NSO input exceeds 512 MiB")
    return uncompressed_nso(parse_nso(raw, MAX_DECODED))


def refresh_hashes(raw):
    """Refresh checked segment digests after the user modifies decoded bytes."""
    out = bytearray(raw)
    require(len(out) >= 256 and out[:4] == b"NSO0", "Expected NSO0")
    flags = u32(out, 12)
    require(not flags & 0x87, "Save requires a decompressed NSO")
    for i in range(3):
        offset, _, size = unpack("<III", out, 16 + 16*i)
        require(offset >= 256 and offset + size <= len(out), "NSO segment outside file")
        if flags & (1 << (i + 3)):
            out[160+32*i:192+32*i] = hashlib.sha256(out[offset:offset+size]).digest()
    return bytes(out)
