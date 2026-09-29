# 86Box patch

`0001-olivetti-pcs286s-support.patch` is a snapshot of the tested implementation
against 86Box commit `53fd57d980f9f6da7f0a23cdb6ce385171e92a41`.

Apply from the root of a matching 86Box checkout:

```powershell
git apply path\to\0001-olivetti-pcs286s-support.patch
```

Place the two local firmware dumps at:

```text
roms/machines/olivetti_pcs286s/PCS286S_REL.1.06_LOW.BIN
roms/machines/olivetti_pcs286s/PCS286S_REL.1.06_HIGH.BIN
```

The patch contains no ROM bytes. It is intended as a reproducible preservation
snapshot and will need rebasing and normal upstream review before submission.
