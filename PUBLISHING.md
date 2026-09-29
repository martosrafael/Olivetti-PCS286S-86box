# Publication and upstream plan

## Public preservation repository

This repository may be made public with the current ignore rules. Before every
release, verify that the following are not tracked:

- original or interleaved ROM binaries;
- virtual hard-disk or floppy images;
- NVR/CMOS files containing a user's local configuration;
- compiled 86Box executables or build directories;
- debug logs containing unrelated local paths or data.

Hashes, analysis, source patches and documentation are intended to be public.

## 86Box upstream sequence

86Box's ROM repository asks contributors to submit machine code to the main 86Box
repository first. The intended sequence is therefore:

1. Rebase the patch onto the current 86Box master branch.
2. Split or tidy the implementation into reviewable commits.
3. Open a pull request against `86Box/86Box` with test evidence.
4. Address maintainer review and get the machine code merged.
5. Open a ROM pull request against `86Box/roms` using the exact filenames expected
   by the merged implementation.
6. Keep this repository as the preservation record, analysis notebook and source
   of provenance even after upstream support lands.

## Evidence for the code pull request

- Photographs or notes confirming the physical CPU, clock, coprocessor and video.
- SHA-256 hashes of both firmware dumps and the interleaved image.
- Screenshots of Resident Diagnostics and MS-DOS 6.22 booting.
- The tested 86Box configuration, excluding disks and personal paths.
- A note that `ROM Checksum Error : 4E` is reproduced by the physical machine.
- A description of each Olivetti-specific KBC and CMOS behavior in the patch.

## Licensing and attribution

The patch modifies GPL-2.0-or-later 86Box code and is offered under the same
license. Project documentation is offered under CC BY-SA 4.0. Firmware remains
copyrighted by its original rightsholder and should be handled through the 86Box
ROM project's established preservation process.
