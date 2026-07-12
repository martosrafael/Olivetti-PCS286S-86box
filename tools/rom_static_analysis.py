#!/usr/bin/env python3
"""Heuristic static analysis for PC/AT-class BIOS ROM images.

This is intentionally lightweight: it does not try to be a full 8086/286
disassembler. It scans for instruction patterns that are especially useful
when bringing a BIOS up in an emulator: reset vector, POST writes and I/O
ports touched through immediate-port instructions or nearby DX loads.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys
from dataclasses import asdict, dataclass


PRINTABLE_RE = re.compile(rb"[\x20-\x7e]{6,}")

PORT_NAMES = {
    0x0000: "DMA controller 1 channel address",
    0x0001: "DMA controller 1 channel address",
    0x0002: "DMA controller 1 channel address",
    0x0003: "DMA controller 1 channel address",
    0x0004: "DMA controller 1 channel address",
    0x0005: "DMA controller 1 channel address",
    0x0006: "DMA controller 1 channel address",
    0x0007: "DMA controller 1 channel address",
    0x0008: "DMA controller 1 command/status",
    0x000A: "DMA controller 1 mask",
    0x000B: "DMA controller 1 mode",
    0x000C: "DMA controller 1 flip-flop",
    0x000D: "DMA controller 1 master clear",
    0x0020: "8259 PIC master command",
    0x0021: "8259 PIC master data",
    0x0040: "8253/8254 PIT channel 0",
    0x0041: "8253/8254 PIT channel 1",
    0x0042: "8253/8254 PIT channel 2",
    0x0043: "8253/8254 PIT control",
    0x0060: "keyboard controller data / PPI port A",
    0x0061: "PPI port B / speaker / refresh",
    0x0064: "keyboard controller status/command",
    0x0070: "CMOS/NMI index",
    0x0071: "CMOS data",
    0x0080: "POST checkpoint / DMA page register",
    0x0092: "system control port A / fast A20",
    0x00A0: "8259 PIC slave command",
    0x00A1: "8259 PIC slave data",
    0x00C0: "DMA controller 2 base",
    0x0170: "secondary fixed disk data",
    0x01F0: "primary fixed disk data",
    0x0278: "parallel port LPT2 data",
    0x02F8: "serial port COM2 base",
    0x0378: "parallel port LPT1 data",
    0x03B4: "MDA/CGA compatible CRTC index",
    0x03B5: "MDA/CGA compatible CRTC data",
    0x03BA: "MDA status",
    0x03C0: "EGA/VGA attribute controller",
    0x03C2: "EGA/VGA misc output",
    0x03C4: "EGA/VGA sequencer index",
    0x03C5: "EGA/VGA sequencer data",
    0x03C7: "VGA DAC read index",
    0x03C8: "VGA DAC write index",
    0x03C9: "VGA DAC data",
    0x03CE: "EGA/VGA graphics controller index",
    0x03CF: "EGA/VGA graphics controller data",
    0x03D4: "CGA/EGA/VGA CRTC index",
    0x03D5: "CGA/EGA/VGA CRTC data",
    0x03DA: "CGA/EGA/VGA status",
    0x03F0: "floppy disk controller status A",
    0x03F1: "floppy disk controller status B",
    0x03F2: "floppy disk controller DOR",
    0x03F4: "floppy disk controller MSR",
    0x03F5: "floppy disk controller data",
    0x03F6: "fixed disk alternate status/control",
    0x03F7: "floppy disk controller DIR / fixed disk status",
    0x03F8: "serial port COM1 base",
}

TERM_HINTS = (
    "OLIVETTI",
    "COPYRIGHT",
    "SETUP",
    "CMOS",
    "KEYBOARD",
    "FLOPPY",
    "DISK",
    "MEMORY",
    "PARITY",
    "ERROR",
    "80287",
    "PASSWORD",
    "SHADOW",
    "EXPANDED",
    "EXTENDED",
)


@dataclass
class ResetInfo:
    offset: int
    bytes_hex: str
    kind: str
    target: str
    target_offset: int | None
    plausible: bool


@dataclass
class PortAccess:
    offset: int
    port: int
    direction: str
    width: int
    form: str
    value: int | None = None


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def physical_base(data: bytes) -> int:
    return 0x100000 - len(data)


def reset_info(data: bytes) -> ResetInfo:
    off = len(data) - 16
    window = data[off : off + 16]
    base = physical_base(data)

    if window and window[0] == 0xEA and len(window) >= 5:
        ip = window[1] | (window[2] << 8)
        cs = window[3] | (window[4] << 8)
        phys = ((cs << 4) + ip) & 0xFFFFF
        target_off = phys - base
        plausible = 0 <= target_off < len(data)
        return ResetInfo(
            off,
            window.hex(" "),
            "far-jump",
            f"{cs:04X}:{ip:04X} phys={phys:05X}",
            target_off if plausible else None,
            plausible,
        )

    return ResetInfo(off, window.hex(" "), "unknown", "", None, False)


def find_mov_dx_before(data: bytes, offset: int, lookback: int = 8) -> int | None:
    start = max(0, offset - lookback)
    for pos in range(offset - 3, start - 1, -1):
        if data[pos] == 0xBA:
            return data[pos + 1] | (data[pos + 2] << 8)
    return None


def scan_ports(data: bytes) -> list[PortAccess]:
    found: list[PortAccess] = []
    for i, op in enumerate(data):
        if op in (0xE4, 0xE5, 0xE6, 0xE7) and i + 1 < len(data):
            port = data[i + 1]
            direction = "in" if op in (0xE4, 0xE5) else "out"
            width = 8 if op in (0xE4, 0xE6) else 16
            value = None
            if direction == "out" and width == 8 and i >= 2 and data[i - 2] == 0xB0:
                value = data[i - 1]
            found.append(PortAccess(i, port, direction, width, "imm8", value))
            continue

        if op in (0xEC, 0xED, 0xEE, 0xEF):
            port = find_mov_dx_before(data, i)
            if port is None:
                continue
            direction = "in" if op in (0xEC, 0xED) else "out"
            width = 8 if op in (0xEC, 0xEE) else 16
            value = None
            if direction == "out" and width == 8 and i >= 2 and data[i - 2] == 0xB0:
                value = data[i - 1]
            found.append(PortAccess(i, port, direction, width, "dx-near-mov", value))
    return found


def term_summary(data: bytes) -> list[dict[str, object]]:
    rows = []
    upper_data = data.upper()
    for term in TERM_HINTS:
        needle = term.encode("ascii")
        offsets = []
        start = 0
        while True:
            idx = upper_data.find(needle, start)
            if idx == -1:
                break
            offsets.append(idx)
            start = idx + len(needle)
        if offsets:
            rows.append(
                {
                    "term": term,
                    "count": len(offsets),
                    "first_offsets": [f"0x{idx:X}" for idx in offsets[:8]],
                }
            )
    return rows


def interesting_strings(data: bytes, limit: int) -> list[dict[str, str | int]]:
    rows: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for match in PRINTABLE_RE.finditer(data):
        raw = match.group(0).decode("ascii", errors="replace")
        text = " ".join(raw.split())
        if text in seen:
            continue
        seen.add(text)
        upper = text.upper()
        if not any(term in upper for term in TERM_HINTS):
            continue
        score = 100 + sum(ch.isalpha() for ch in text)
        rows.append((score, match.start(), text))

    best = sorted(rows, key=lambda row: (-row[0], row[1]))[:limit]
    return [
        {"offset": offset, "offset_hex": f"0x{offset:X}", "text": text}
        for _score, offset, text in sorted(best, key=lambda row: row[1])
    ]


def summarize_ports(accesses: list[PortAccess]) -> list[dict[str, object]]:
    by_port: dict[int, list[PortAccess]] = collections.defaultdict(list)
    for access in accesses:
        by_port[access.port].append(access)

    rows = []
    for port, items in sorted(by_port.items()):
        directions = ",".join(sorted({i.direction for i in items}))
        forms = ",".join(sorted({i.form for i in items}))
        rows.append(
            {
                "port": port,
                "port_hex": f"0x{port:04X}" if port > 0xFF else f"0x{port:02X}",
                "count": len(items),
                "directions": directions,
                "forms": forms,
                "name": PORT_NAMES.get(port, ""),
                "first_offsets": [f"0x{i.offset:X}" for i in items[:8]],
            }
        )
    return rows


def post_candidates(accesses: list[PortAccess]) -> list[dict[str, object]]:
    posts = [
        access
        for access in accesses
        if access.port == 0x80 and access.direction == "out" and access.value is not None
    ]
    rows = []
    seen: set[tuple[int, int | None]] = set()
    for access in posts:
        key = (access.offset, access.value)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "offset": access.offset,
                "offset_hex": f"0x{access.offset:X}",
                "value": access.value,
                "value_hex": f"0x{access.value:02X}",
                "form": access.form,
            }
        )
    return rows


def markdown_report(analysis: dict[str, object], include_strings: bool) -> str:
    lines: list[str] = []
    lines.append("# BIOS static analysis")
    lines.append("")
    lines.append("This report contains derived facts only; ROM binaries are kept local.")
    lines.append("")
    lines.append("## Image")
    lines.append("")
    lines.append(f"- Path: `{analysis['path']}`")
    lines.append(f"- Size: {analysis['size']} bytes / `{analysis['size_hex']}`")
    lines.append(f"- SHA-256: `{analysis['sha256']}`")
    lines.append(f"- Assumed physical base: `{analysis['physical_base_hex']}`")
    lines.append(f"- 8-bit checksum: `{analysis['sum8_hex']}`")
    lines.append(f"- 16-bit checksum: `{analysis['sum16_hex']}`")
    lines.append("")

    reset = analysis["reset"]
    assert isinstance(reset, dict)
    lines.append("## Reset Vector")
    lines.append("")
    lines.append(f"- Offset: `{reset['offset_hex']}`")
    lines.append(f"- Bytes: `{reset['bytes_hex']}`")
    lines.append(f"- Decode: {reset['kind']} {reset['target']}".rstrip())
    lines.append(f"- Target image offset: `{reset['target_offset_hex']}`")
    lines.append(f"- Plausible: `{str(reset['plausible']).lower()}`")
    lines.append("")

    lines.append("## String Signals")
    lines.append("")
    lines.append("| Term | Count | First offsets |")
    lines.append("| --- | ---: | --- |")
    for row in analysis["string_terms"]:
        assert isinstance(row, dict)
        offsets = ", ".join(row["first_offsets"])
        lines.append(f"| `{row['term']}` | {row['count']} | {offsets} |")
    if include_strings:
        lines.append("")
        lines.append("### Local String Excerpts")
        lines.append("")
        lines.append("These excerpts are for private local debugging only.")
        lines.append("")
        for item in analysis["strings"]:
            assert isinstance(item, dict)
            text = str(item["text"])
            if len(text) > 96:
                text = text[:93] + "..."
            lines.append(f"- `{item['offset_hex']}`: {text}")
    else:
        lines.append("")
        lines.append("Direct ROM string excerpts are omitted from this report. Use `--include-strings` for local debugging.")
    lines.append("")

    lines.append("## Known I/O Ports Seen")
    lines.append("")
    lines.append("| Port | Count | Dir | Meaning | First offsets |")
    lines.append("| --- | ---: | --- | --- | --- |")
    known_rows = [row for row in analysis["ports"] if row["name"]]
    for row in known_rows:
        offsets = ", ".join(row["first_offsets"])
        lines.append(
            f"| `{row['port_hex']}` | {row['count']} | {row['directions']} | {row['name']} | {offsets} |"
        )
    lines.append("")

    lines.append("## Probable POST Writes")
    lines.append("")
    posts = analysis["post_candidates"]
    if posts:
        preview = posts[:64]
        lines.append("| Offset | Value | Form |")
        lines.append("| --- | --- | --- |")
        for row in preview:
            assert isinstance(row, dict)
            lines.append(f"| `{row['offset_hex']}` | `{row['value_hex']}` | {row['form']} |")
        if len(posts) > len(preview):
            lines.append(f"| ... | ... | {len(posts) - len(preview)} more omitted |")
    else:
        lines.append("No immediate `OUT 80h, AL` checkpoint pattern found.")
    lines.append("")

    lines.append("## Emulator Bring-up Notes")
    lines.append("")
    lines.append("- The reset vector supports mapping this 128 KiB BIOS at physical `0xE0000-0xFFFFF`.")
    lines.append("- The BIOS clearly expects AT-class services: CMOS, 8042 keyboard controller, PIC, PIT, DMA, FDC and fixed disk ports appear in static scans.")
    lines.append("- The static port scan is heuristic and can include table/data false positives; use it to decide what to trace first, not as a final hardware map.")
    lines.append("- If 86Box hangs after video text appears, the first suspects are CMOS contents, keyboard-controller commands, disk-controller readiness and any Olivetti-specific setup register.")
    lines.append("")
    return "\n".join(lines)


def analyze(path: pathlib.Path, strings_limit: int) -> dict[str, object]:
    data = path.read_bytes()
    reset = reset_info(data)
    reset_dict = asdict(reset)
    reset_dict["offset_hex"] = f"0x{reset.offset:X}"
    reset_dict["target_offset_hex"] = (
        f"0x{reset.target_offset:X}" if reset.target_offset is not None else ""
    )

    accesses = scan_ports(data)
    return {
        "path": str(path),
        "size": len(data),
        "size_hex": f"0x{len(data):X}",
        "sha256": sha256_hex(data),
        "physical_base": physical_base(data),
        "physical_base_hex": f"0x{physical_base(data):05X}",
        "sum8": sum(data) & 0xFF,
        "sum8_hex": f"0x{sum(data) & 0xFF:02X}",
        "sum16": sum(data) & 0xFFFF,
        "sum16_hex": f"0x{sum(data) & 0xFFFF:04X}",
        "reset": reset_dict,
        "string_terms": term_summary(data),
        "strings": interesting_strings(data, strings_limit),
        "ports": summarize_ports(accesses),
        "post_candidates": post_candidates(accesses),
    }


def command_analyze(args: argparse.Namespace) -> int:
    result = analyze(pathlib.Path(args.rom), args.strings)

    if args.json_out:
        pathlib.Path(args.json_out).write_text(json.dumps(result, indent=2), encoding="utf-8")

    report = markdown_report(result, args.include_strings)
    if args.out:
        pathlib.Path(args.out).write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", help="Combined BIOS ROM image")
    parser.add_argument("--out", help="Write Markdown report to this path")
    parser.add_argument("--json-out", help="Optional JSON output path")
    parser.add_argument("--strings", type=int, default=40)
    parser.add_argument(
        "--include-strings",
        action="store_true",
        help="Include short direct BIOS string excerpts in the Markdown report.",
    )
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return command_analyze(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
