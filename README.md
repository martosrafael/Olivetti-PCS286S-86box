# Olivetti PCS 286S para 86Box

Kit limpio para reconstruir una emulacion del Olivetti PCS 286S en 86Box a partir de los dos chips de BIOS originales.

## Estado actual

- No hay dumps reales incluidos en este kit.
- La herramienta `tools/bios_tool.py` permite inspeccionar los chips, generar las dos combinaciones posibles de BIOS de 16 bits y detectar cual tiene un vector de reset mas plausible.
- La integracion con 86Box esta documentada como flujo de trabajo, no como parche final, porque antes necesitamos ver el contenido real de los dumps y el punto exacto donde se queda colgada la BIOS.

## Estructura

```text
dumps/
  original/        # pon aqui los dos chips originales, sin modificar
  derived/         # aqui se generan BIOS combinadas e informes
notes/
  86box-integration.md
  bringup-plan.md
  hardware-notes.md
patches/
  86box/           # notas para el futuro parche de 86Box
tools/
  bios_tool.py
vm/
  README.md
```

## Primer paso con tus dumps

Copia los dos ficheros de BIOS a:

```text
dumps/original/
```

Por ejemplo:

```text
dumps/original/chip-uXX.bin
dumps/original/chip-uYY.bin
```

Despues, desde la raiz de este kit:

```powershell
tools\run_bios_tool.cmd inspect dumps\original\chip-uXX.bin dumps\original\chip-uYY.bin
tools\run_bios_tool.cmd candidates dumps\original\chip-uXX.bin dumps\original\chip-uYY.bin --out dumps\derived
```

La segunda orden genera:

- `candidate_a_low_even.bin`
- `candidate_b_low_even.bin`
- `candidate_report.md`
- `candidate_manifest.json`

El candidato bueno suele ser el que tiene bytes de reset coherentes en los ultimos 16 bytes del fichero. En muchas BIOS AT aparece un salto lejano (`EA xx xx xx F0`) cerca de la direccion fisica `FFFF0`, pero no conviene asumirlo hasta inspeccionar el dump real.

Para sacar un resumen estatico util para el port a 86Box:

```powershell
tools\run_bios_tool.cmd candidates dumps\original\chip-uXX.bin dumps\original\chip-uYY.bin --out dumps\derived
tools\run_rom_static_analysis.cmd dumps\derived\candidate_a_low_even.bin --out notes\bios-analysis.md
```

## Objetivo tecnico

El objetivo no es solo "que arranque algo", sino dejar tres piezas reproducibles:

1. Dumps originales identificados por tamano y SHA-256.
2. BIOS combinada documentada, con orden de chips justificado.
3. Parche de 86Box minimo, primero basado en una maquina AT 286 parecida y despues ajustado a los puertos/dispositivos que la BIOS del Olivetti espere.

## Datos que me faltan

Cuando puedas, trae estos datos:

- Los dos dumps de BIOS.
- Si lo recuerdas: que nombres/etiquetas tenian los chips en la placa.
- Captura o texto de lo ultimo que muestra la BIOS antes de quedarse colgada.
- Si el intento anterior tenia algun parche, config de 86Box o ROM combinada, tambien ayuda aunque este desordenado.
