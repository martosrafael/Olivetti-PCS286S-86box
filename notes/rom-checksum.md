# ROM checksum investigation

## Observed behavior

Both the physical Olivetti PCS 286S and 86Box display:

```text
ROM Checksum Error : 4E
```

The machine then continues into Resident Diagnostics and can boot normally. This
matching behavior is evidence that the emulator is reading the same firmware state
as the physical machine, not evidence of an emulation failure.

## What `4E` means

Disassembly shows that the firmware writes `0x4E` to I/O port `0x378` as a POST
checkpoint. It is not the calculated checksum value.

The checksum routine separately sums 16-bit words over two 64 KiB regions:

| Physical region | 16-bit additive sum | Expected |
| --- | ---: | ---: |
| `E0000-EFFFF` | `0x1000` | `0x0000` |
| `F0000-FFFFF` | `0x0000` | `0x0000` |

The lower firmware half therefore fails the BIOS's own test while the upper half
passes it.

## Interpretation

A stable EPROM bit that has changed from 0 to 1 through ageing is plausible. The
`0x1000` residual is compatible with one `0x10` bit in the high/odd EPROM within
the first 32 KiB. A historical factory or service patch without corrected checksum
is also possible. The current evidence cannot distinguish those explanations.

Repeatedly dumping the same chips can establish read stability, but cannot prove
what the original factory bytes were. A second independent PCS 286S BIOS Release
1.06 dump is needed for that comparison.

## Preservation rule

Do not alter or reprogram the original EPROMs. Preserve multiple verified copies
of each dump. Checksum experiments should use derived files in emulation first and,
if physical testing is justified, newly programmed compatible EPROMs or adapters.
