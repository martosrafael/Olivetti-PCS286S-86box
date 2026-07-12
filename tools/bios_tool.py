#!/usr/bin/env python3
"""Small BIOS dump helper for the Olivetti PCS 286S 86Box project."""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import re
import sys
from dataclasses import dataclass, asdict


PRINTABLE_RE = re.compile(rb"[\x20-\x7e]{6,}")
INTERESTING_TERMS = (
    "OLIVETTI",
    "COPYRIGHT",
    "BIOS",
    "PCS",
    "286",
    "CMOS",
    "KEYBOARD",
    "DISK",
    "FLOPPY",
    "ERROR",
    "SETUP",
    "MEMORY",
    "PARITY",
    "TIMER",
    "ROM",
    "RAM",
)


@dataclass
class ResetVector:
    offset: int
    bytes_hex: str
    kind: str
    target: str
    plausible: bool


@dataclass
class RomInfo:
    path: str
    size: int
    sha256: str
    reset_vector: ResetVector
    strings: list[str]


def read_file(path: pathlib.Path) -> bytes:
    try:
        return path.read_bytes()
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}") from None


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reset_vector_info(data: bytes) -> ResetVector:
    if len(data) < 16:
        return ResetVector(0, data.hex(" "), "too-small", "", False)

    off = len(data) - 16
    window = data[off : off + 16]
    op = window[0]

    if op == 0xEA and len(window) >= 5:
        ip = window[1] | (window[2] << 8)
        cs = window[3] | (window[4] << 8)
        phys = ((cs << 4) + ip) & 0xFFFFF
        plausible = 0xF0000 <= phys <= 0xFFFFF
        return ResetVector(
            off,
            window.hex(" "),
            "far-jump",
            f"{cs:04X}:{ip:04X} phys={phys:05X}",
            plausible,
        )

    if op == 0xE9 and len(window) >= 3:
        rel = int.from_bytes(window[1:3], "little", signed=True)
        target = (off + 3 + rel) & 0xFFFFF
        plausible = len(data) - 0x10000 <= target < len(data)
        return ResetVector(
            off,
            window.hex(" "),
            "near-jump",
            f"relative={rel:+d} image-offset={target:05X}",
            plausible,
        )

    if op == 0xEB and len(window) >= 2:
        rel = int.from_bytes(window[1:2], "little", signed=True)
        target = (off + 2 + rel) & 0xFFFFF
        plausible = len(data) - 0x10000 <= target < len(data)
        return ResetVector(
            off,
            window.hex(" "),
            "short-jump",
            f"relative={rel:+d} image-offset={target:05X}",
            plausible,
        )

    return ResetVector(off, window.hex(" "), "unknown", "", False)


def extract_strings(data: bytes, limit: int) -> list[str]:
    scored: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for match in PRINTABLE_RE.finditer(data):
        text = match.group(0).decode("ascii", errors="replace")
        normalized = " ".join(text.split())
        if normalized in seen:
            continue
        seen.add(normalized)

        upper = normalized.upper()
        letters = sum(ch.isalpha() for ch in normalized)
        spaces = normalized.count(" ")
        distinct = len(set(normalized))
        term_bonus = 100 if any(term in upper for term in INTERESTING_TERMS) else 0
        word_bonus = 20 if spaces and letters >= 4 else 0
        repeated_penalty = 40 if distinct < 4 else 0
        score = term_bonus + word_bonus + letters + spaces - repeated_penalty

        if score <= 0:
            continue

        offset_text = f"0x{match.start():X}: {normalized}"
        scored.append((score, match.start(), offset_text))

    best = sorted(scored, key=lambda item: (-item[0], item[1]))[:limit]
    found = []
    for _score, _offset, text in sorted(best, key=lambda item: item[1]):
        if text not in seen:
            found.append(text)
    return found


def inspect_rom(path: pathlib.Path, strings_limit: int) -> RomInfo:
    data = read_file(path)
    return RomInfo(
        path=str(path),
        size=len(data),
        sha256=sha256_hex(data),
        reset_vector=reset_vector_info(data),
        strings=extract_strings(data, strings_limit),
    )


def interleave(low_even: bytes, high_odd: bytes) -> bytes:
    if len(low_even) != len(high_odd):
        raise SystemExit(
            "The two chips have different sizes. Stop here and verify the dumps."
        )

    out = bytearray(len(low_even) * 2)
    out[0::2] = low_even
    out[1::2] = high_odd
    return bytes(out)


def write_report(infos: list[RomInfo], candidates: list[RomInfo], out: pathlib.Path) -> None:
    lines: list[str] = []
    lines.append("# BIOS candidate report")
    lines.append("")
    lines.append(f"Generated: {_dt.datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("## Input chips")
    lines.append("")
    for info in infos:
        lines.extend(format_info_markdown(info, include_strings=False))
        lines.append("")
    lines.append("## Combined candidates")
    lines.append("")
    for info in candidates:
        lines.extend(format_info_markdown(info, include_strings=True))
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


def format_info_markdown(info: RomInfo, include_strings: bool) -> list[str]:
    rv = info.reset_vector
    lines = [
        f"### `{pathlib.Path(info.path).name}`",
        "",
        f"- Size: {info.size} bytes / 0x{info.size:X}",
        f"- SHA-256: `{info.sha256}`",
        f"- Reset vector offset: 0x{rv.offset:X}",
        f"- Reset vector bytes: `{rv.bytes_hex}`",
        f"- Reset vector decode: {rv.kind} {rv.target}".rstrip(),
        f"- Reset vector plausible: `{str(rv.plausible).lower()}`",
    ]
    if include_strings:
        lines.append("- Strings:")
        if info.strings:
            for item in info.strings:
                lines.append(f"  - `{item}`")
        else:
            lines.append("  - none found")
    return lines


def print_info(info: RomInfo) -> None:
    print(f"{info.path}")
    print(f"  size: {info.size} bytes / 0x{info.size:X}")
    print(f"  sha256: {info.sha256}")
    rv = info.reset_vector
    print(f"  reset[{rv.offset:#x}]: {rv.bytes_hex}")
    print(f"  reset decode: {rv.kind} {rv.target}".rstrip())
    print(f"  reset plausible: {rv.plausible}")
    if info.strings:
        print("  strings:")
        for text in info.strings:
            print(f"    {text}")


def command_inspect(args: argparse.Namespace) -> int:
    infos = [inspect_rom(pathlib.Path(p), args.strings) for p in args.paths]
    if args.json:
        print(json.dumps([asdict(i) for i in infos], indent=2))
    else:
        for info in infos:
            print_info(info)
    return 0


def command_candidates(args: argparse.Namespace) -> int:
    chip_a_path = pathlib.Path(args.chip_a)
    chip_b_path = pathlib.Path(args.chip_b)
    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    chip_a = read_file(chip_a_path)
    chip_b = read_file(chip_b_path)

    candidates = [
        ("candidate_a_low_even.bin", interleave(chip_a, chip_b)),
        ("candidate_b_low_even.bin", interleave(chip_b, chip_a)),
    ]

    candidate_infos: list[RomInfo] = []
    for name, data in candidates:
        path = out_dir / name
        path.write_bytes(data)
        candidate_infos.append(inspect_rom(path, args.strings))

    input_infos = [
        inspect_rom(chip_a_path, args.strings),
        inspect_rom(chip_b_path, args.strings),
    ]

    manifest = {
        "generated": _dt.datetime.now().isoformat(timespec="seconds"),
        "meaning": "low_even means this chip occupies even byte addresses on the 16-bit data bus",
        "inputs": [asdict(i) for i in input_infos],
        "candidates": [asdict(i) for i in candidate_infos],
    }
    (out_dir / "candidate_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    write_report(input_infos, candidate_infos, out_dir / "candidate_report.md")

    for info in candidate_infos:
        print_info(info)
    print(f"\nWrote report: {out_dir / 'candidate_report.md'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect and combine two 8-bit BIOS chips for a 286-class PC."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="Inspect one or more ROM binaries")
    inspect.add_argument("paths", nargs="+")
    inspect.add_argument("--strings", type=int, default=24)
    inspect.add_argument("--json", action="store_true")
    inspect.set_defaults(func=command_inspect)

    candidates = sub.add_parser(
        "candidates",
        help="Generate both possible even/odd interleavings from two chip dumps",
    )
    candidates.add_argument("chip_a")
    candidates.add_argument("chip_b")
    candidates.add_argument("--out", default="dumps/derived")
    candidates.add_argument("--strings", type=int, default=32)
    candidates.set_defaults(func=command_candidates)

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
