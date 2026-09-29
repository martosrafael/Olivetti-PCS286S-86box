# Tested 86Box configuration

The following settings reproduce the validated machine without publishing a disk,
NVR file or user-specific path:

```ini
[Machine]
machine = olivetti_pcs286s
cpu_family = 286
cpu_speed = 16000000
mem_size = 2048
fpu_type = 287xl

[Video]
gfxcard = pvga1a

[Floppy and CD-ROM drives]
fdd_01_type = 35_2hd
```

The physical system has an 80287. `287xl` is the tested 86Box selection; confirm
the exact physical coprocessor variant from its package markings before treating
that subtype as a hardware fact.

Start a VM with explicit local paths:

```powershell
86Box.exe --vmpath C:\path\to\vm --rompath C:\path\to\roms
```

CMOS/NVR data is stored by 86Box under the VM path. Back up that directory when
preserving an installed system, but do not commit personal VM state here.
