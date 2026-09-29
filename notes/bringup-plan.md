# Bring-up record

This file records the completed milestones that turned the initial firmware dump
into a booting 86Box machine.

1. Identified the even/odd order of the two 64 KiB EPROM dumps.
2. Mapped the combined 128 KiB image at `0xE0000-0xFFFFF`.
3. Selected Paradise PVGA1A to match the integrated VGA family.
4. Reproduced the real machine's ROM checksum message and reached diagnostics.
5. Implemented the Olivetti KBC command behavior needed to complete POST.
6. Corrected CMOS memory fields so 2048 KB means 640 KB base plus 1408 KB extended.
7. Corrected CMOS equipment bits for floppy and 80287 presence.
8. Verified persistent CMOS data and eliminated the spurious configuration error.
9. Installed and booted MS-DOS 6.22 from a virtual hard disk.

## Remaining upstream work

- Capture clean screenshots and a minimal configuration for review.
- Rebase and clean the patch against current 86Box master.
- Submit the code pull request to 86Box.
- Submit the firmware to the official 86Box ROM repository after code acceptance.
- Compare with a second independent BIOS Release 1.06 dump if one is found.
