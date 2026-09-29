# BIOS modification workflow

A modified BIOS can be developed in 86Box and later tested on the physical PCS
286S, but emulator success is necessary rather than sufficient. 86Box does not
model every electrical, timing or proprietary hardware detail.

## Non-negotiable preservation rules

- Never erase or reprogram the two original EPROMs.
- Keep several read-only copies of the original dumps and their published hashes.
- Work only on derived images under version control.
- Use replacement devices whose capacity, pinout, voltage and access time have
  been checked against the exact markings on the original chips.
- Program chips out of circuit and verify a complete read-back before installation.

## Image workflow

1. Interleave `LOW` on even addresses and `HIGH` on odd addresses to produce the
   128 KiB development image.
2. Make the smallest possible patch and record every changed offset.
3. Recalculate the firmware's checksums. This BIOS separately expects the 16-bit
   additive sum of `E0000-EFFFF` and `F0000-FFFFF` to equal zero.
4. Test cold boot, warm reset, Resident Diagnostics, setup, CMOS persistence,
   keyboard, floppy, VGA, hard disk, memory and 80287 behavior in 86Box.
5. Split the final 128 KiB image back into even-address bytes for `LOW` and
   odd-address bytes for `HIGH`.
6. Program two replacement chips and read them back byte for byte. Compare hashes
   with the intended split images before installing them.

## First physical test

- Photograph and label chip orientation and socket position before removal.
- Store the original pair safely and use only the verified replacement pair.
- Disconnect irreplaceable storage for the first boot and use a known expendable
  floppy or disk configuration.
- Keep the original pair ready so recovery means powering off and restoring them.

A failed code experiment will normally only prevent boot and is recoverable by
restoring the original EPROMs. A chip with the wrong electrical specification or
orientation can damage hardware, so those checks cannot be delegated to emulation.

Do not "repair" the existing checksum residual by changing an arbitrary byte in
the preservation dump. First obtain another independent Release 1.06 dump or make
an intentional, documented firmware change whose checksum compensation is part of
that derived experimental build.
