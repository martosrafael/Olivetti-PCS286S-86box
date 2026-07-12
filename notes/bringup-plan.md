# 86Box bring-up plan

## Current BIOS facts

- BIOS release: local dumps named `PCS286S_REL.1.06_LOW.BIN` and `PCS286S_REL.1.06_HIGH.BIN`.
- Correct interleave: `LOW` on even addresses, `HIGH` on odd addresses.
- Combined image size: 128 KiB.
- Expected physical mapping: `0xE0000-0xFFFFF`.
- Reset vector: image offset `0x1FFF0`, far jump to `F000:E05B` / physical `0xFE05B`.
- Combined SHA-256: `88ef6bf52e6c1aea6f7612faef1989702f3a500ee3312ddef5a590b68c63909a`.

## First 86Box target

Start with the smallest possible 286 AT-style machine definition:

- 80286 CPU.
- AT-compatible PIC, PIT, DMA and 8042 keyboard controller.
- MC146818-compatible CMOS/RTC.
- Standard FDC at `0x3F0-0x3F7`.
- Fixed disk controller present but initially optional.
- Conventional video adapter selected through existing 86Box options.
- 128 KiB BIOS ROM mapped from `0xE0000`.

The first success criterion is not booting DOS. It is reaching a stable BIOS/setup screen or a repeatable POST/error state with a known checkpoint.

## Trace first

Instrument or enable logs around these areas first:

- POST writes to port `0x80`.
- CMOS index/data ports `0x70/0x71`.
- Keyboard controller ports `0x60/0x64`.
- PIT/PIC/DMA initialization.
- FDC ports `0x3F2`, `0x3F4`, `0x3F5`, `0x3F7`.
- Video adapter probing around EGA/VGA compatible ports.

## Likely hang causes

The static BIOS scan points to these likely failure modes:

- CMOS checksum or configuration mismatch causing a setup/error path.
- Keyboard controller command/status behavior differing from what the Olivetti BIOS expects.
- Video configuration mismatch, including a motherboard/video jumper concept.
- FDC or fixed-disk readiness wait loop.
- An Olivetti-specific setup/configuration port not yet identified.

## Next concrete steps

1. Get a local 86Box source tree or fork.
2. Identify the closest existing 286 AT machine implementation.
3. Add a minimal `olivetti_pcs286s` machine entry that loads a 128 KiB BIOS.
4. Add temporary POST/CMOS/KBC tracing.
5. Boot with conservative RAM and no hard disk first.
6. Record the last POST code, last text on screen and last repeated I/O access.

