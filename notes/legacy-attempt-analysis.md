# Legacy attempt analysis

Source inspected:

```text
D:\pcs286s\86box
D:\pcs286s\86box\build\src
```

This was not a Git repository, but it contained useful backup files:

- `src/machine/m_at_286_old.c`
- `src/machine/machine_table_old.c`
- runtime logs in `build/src/`

## Useful facts recovered

- The previous build loaded the PCS 286S BIOS successfully.
- The ROM load path was:
  - `roms/machines/olivetti_pcs286s/PCS286S_REL.1.06_LOW.bin`
  - `roms/machines/olivetti_pcs286s/PCS286S_REL.1.06_HIGH.bin`
- It used `bios_load_interleaved(..., 0x000e0000, 131072, 0)`.
- The log repeatedly reported `bios_load_interleaved ret=1`, so ROM loading was not the blocker.
- The old machine entry used a 286 AT-like model with Olivetti KBC parameters.
- The old init eventually used the SCAT path plus `f82c710_device` and `ide_isa_device`.

## Hacks found

The legacy tree had several debugging or brute-force patches:

- Global I/O logging in `src/cpu/x86_ops_io.h`.
- CMOS/NVR logging and forced reads in `src/nvr_at.c`.
- Extra KBC command handling in `src/device/kbc_at.c`.
- POST and VGA write logging inside `src/machine/m_at_286.c`.
- A global removal of the max-RAM cap in `machine_get_max_ram`.

These are useful clues, but they should not be carried into the clean patch as-is.

## KBC/CMOS clues

The final logs point to a keyboard-controller loop, not a simple ROM mapping failure.

Recurring KBC patterns near the hang:

```text
OUT 0064 -> CF
IN  0064 -> 1E / 1D
OUT 0064 -> 82 or 8B or 80
IN  0060 -> 55 or 8C
```

The old KBC hack handled:

- command `0x80`: return `0x8C`
- command `0x8A`: return `0x8C`
- command `0x8B`: return `0x8C`
- command `0xCF`: return `0x55`

The current upstream 86Box already has `KBC_VEN_OLIVETTI`, but its Olivetti handler only handles command `0x80`. This is the likely next place to investigate after the clean machine-entry patch.

CMOS clues:

- The old NVR patch forced register `0x0D` / `0x8D` to return `0x80`.
- It forced register `0x14` / `0x94` to return `0x00`.
- Final debug logs also show reads of CMOS registers `0x0E`, `0x1E`, `0x7F`, `0x1D`, `0x20`, `0x21`, `0x17`, and `0x18`.

## Current clean approach

Patch `0001-add-olivetti-pcs286s-machine.patch` intentionally includes only:

- the PCS 286S BIOS config/device;
- a machine table entry;
- a 128 KiB interleaved BIOS mapping at `0xE0000`;
- SCAT-style initialization with Olivetti KBC parameters;
- FDC, `f82c710` and ISA IDE devices.

It intentionally does not include the KBC/CMOS hacks. The next run should tell us whether upstream Olivetti KBC support is already enough, or whether commands `0x8A`, `0x8B`, `0x82` and `0xCF` need a proper implementation.

