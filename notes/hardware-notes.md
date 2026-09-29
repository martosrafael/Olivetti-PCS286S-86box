# Reference hardware

These facts describe the physical Olivetti PCS 286S used for this preservation
work. Unknown details are intentionally left unstated rather than inferred.

| Component | Observed configuration |
| --- | --- |
| CPU | Intel-compatible 80286 |
| Clock | 16 MHz |
| Coprocessor | 80287 installed |
| RAM used for validation | 2048 KB total |
| Conventional RAM | 640 KB |
| Extended RAM | 1408 KB |
| Video | Integrated Paradise VGA; emulated with PVGA1A |
| Floppy | 3.5-inch high-density drive |
| Firmware | Olivetti Release 1.06, two 64 KiB EPROMs |
| Diagnostics | Resident Diagnostics Rev. 1.06 |

## Physical-machine observations

- Startup prints `ROM Checksum Error : 4E` and then continues.
- Resident Diagnostics tests CPU, ROM, memory refresh, keyboard controller,
  interrupt controllers, DMA controllers, keyboard, clock/calendar, protected mode
  and CMOS RAM.
- The physical machine has an 80287 coprocessor.
- The system has a built-in extended setup used to allocate extended and expanded
  memory and configure shadow memory.

## Firmware dump identity

- `LOW`: SHA-256 `cc13e38fa673b9ecf0e6fb75562b2eda74a2d2ed2fa7e2ce04b477300a3034ed`
- `HIGH`: SHA-256 `d01e13cc4cd2dfaf1ab60ad98670883a309ab930f212c17d22a1db7890511a6a`
- Combined: SHA-256 `88ef6bf52e6c1aea6f7612faef1989702f3a500ee3312ddef5a590b68c63909a`

Label photographs, motherboard revisions and controller-chip markings would improve
future hardware accuracy and should be added when the case is next opened.
