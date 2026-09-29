# 86Box integration

## Tested base

- 86Box upstream commit: `53fd57d980f9f6da7f0a23cdb6ce385171e92a41`
- Machine identifier: `olivetti_pcs286s`
- Firmware mapping: 128 KiB at physical `0xE0000-0xFFFFF`
- Firmware files: `PCS286S_REL.1.06_LOW.BIN` and
  `PCS286S_REL.1.06_HIGH.BIN`, interleaved by the existing ROM loader

## Machine-specific behavior

The implementation is based on 86Box's AT 286 infrastructure and adds only the
behavior required by this firmware:

- an Olivetti-specific keyboard controller device and commands used during POST;
- a no-response path for command `0x82`, avoiding an unnecessary POST timeout;
- CMOS synchronization for total memory, extended/expanded allocation, floppy
  presence and coprocessor presence;
- CMOS checksum regeneration after synchronized values change;
- Olivetti NVR register `0x7F` behavior required by the early firmware path;
- a fixed 16 MHz machine entry.

## Validated result

With 2048 KB selected in 86Box, POST reports 640 KB base plus 1408 KB extended.
Resident Diagnostics completes without the previous system-configuration mismatch,
and MS-DOS 6.22 installs and boots. Paradise PVGA1A is used for the integrated VGA.

The current patch is a preservation snapshot, not yet an upstream-quality commit.
Before opening a pull request it should be rebased, reviewed against current 86Box
style and split if maintainers prefer separate machine, KBC and CMOS changes.
