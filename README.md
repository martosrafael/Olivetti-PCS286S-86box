# Olivetti PCS 286S preservation and 86Box support

This project preserves the firmware, hardware findings and 86Box work needed to
emulate an Olivetti PCS 286S. The reference machine is a real 16 MHz 80286 system
with an 80287 coprocessor, integrated Paradise VGA and Olivetti BIOS Release 1.06.

The current implementation completes Resident Diagnostics, reports the configured
2048 KB of RAM correctly, retains CMOS settings and boots MS-DOS 6.22.

[Resumen en espanol](README.es.md)

## Why this repository exists

The PCS 286S is poorly represented in current emulation projects. This repository
keeps the evidence and implementation reproducible so support does not depend on
one computer, one set of EPROMs or one private build.

The intended final home is upstream 86Box:

1. Submit the machine implementation to the
   [86Box project](https://github.com/86Box/86Box).
2. Once the code is merged, submit the matching firmware to the official
   [86Box ROM repository](https://github.com/86Box/roms), following its rules.

## Current status

- BIOS Release 1.06 loads from two 64 KiB EPROM images.
- The images are interleaved into a 128 KiB ROM mapped at `E0000-FFFFF`.
- The machine is fixed at its real 16 MHz clock.
- The Olivetti keyboard-controller extensions required by POST are implemented.
- CMOS memory, floppy and coprocessor data are synchronized with 86Box settings.
- A 2048 KB configuration is reported as 640 KB base plus 1408 KB extended.
- Resident Diagnostics completes and MS-DOS 6.22 boots from a virtual disk.
- The original machine and emulation both display `ROM Checksum Error : 4E` before
  continuing. This is documented in [the checksum analysis](notes/rom-checksum.md).

## Repository layout

```text
dumps/       local ROM inputs and generated images; binaries are ignored by Git
notes/       hardware, firmware and reverse-engineering findings
patches/     the current 86Box patch
tools/       ROM interleaving and static-analysis utilities
vm/          reproducible 86Box configuration notes
```

## Firmware identity

The binary dumps are deliberately not stored in this general-purpose repository.
Their identities are published so independently preserved copies can be verified:

| Image | Size | SHA-256 |
| --- | ---: | --- |
| `PCS286S_REL.1.06_LOW.BIN` | 65536 | `cc13e38fa673b9ecf0e6fb75562b2eda74a2d2ed2fa7e2ce04b477300a3034ed` |
| `PCS286S_REL.1.06_HIGH.BIN` | 65536 | `d01e13cc4cd2dfaf1ab60ad98670883a309ab930f212c17d22a1db7890511a6a` |
| Interleaved ROM | 131072 | `88ef6bf52e6c1aea6f7612faef1989702f3a500ee3312ddef5a590b68c63909a` |

`LOW` occupies even addresses and `HIGH` occupies odd addresses. The reset vector
at image offset `0x1FFF0` is `EA 5B E0 00 F0`, a far jump to `F000:E05B`.

## Reproducing the ROM image

Place verified local dumps under `dumps/original/`, then run:

```powershell
tools\run_bios_tool.cmd candidates `
  dumps\original\PCS286S_REL.1.06_LOW.BIN `
  dumps\original\PCS286S_REL.1.06_HIGH.BIN `
  --out dumps\derived
```

The expected image is `dumps/derived/candidate_a_low_even.bin`.

## Credits

- Original hardware, firmware dumps, physical-machine observations and testing:
  Rafael (`@martosrafael`).
- 86Box implementation and reverse-engineering work: developed collaboratively
  by Rafael and OpenAI Codex, based on the existing 86Box codebase.
- 86Box and its contributors provide the emulator this work extends.

This is an independent preservation project and is not affiliated with Olivetti.
See [PUBLISHING.md](PUBLISHING.md) for the upstream and release plan.
