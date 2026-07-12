# Dumps derivados

Aqui se generan las BIOS combinadas y los informes:

```powershell
tools\run_bios_tool.cmd candidates dumps\original\chip-uXX.bin dumps\original\chip-uYY.bin --out dumps\derived
```

Los binarios derivados tambien quedan fuera de Git. Los informes `.md` y `.json` pueden subirse si no contienen datos que prefieras mantener privados.

