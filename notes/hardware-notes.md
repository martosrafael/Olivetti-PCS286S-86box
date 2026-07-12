# Olivetti PCS 286S - notas pendientes

Rellenar cuando tengamos la maquina o fotos/documentacion:

- CPU:
- Frecuencia:
- Chipset:
- Controlador de teclado:
- Controlador de disquete:
- Controlador de disco:
- Video original:
- Tamano de RAM base:
- Tamano de RAM extendida:
- Etiquetas de los chips BIOS:
- Tamano de cada chip:
- Fecha/cadena de version de BIOS:

## Observaciones de arranque

Anotar aqui cada prueba:

```text
Fecha:
86Box version:
BIOS usada:
Maquina base:
Video:
RAM:
Ultimo texto en pantalla:
Ultimo codigo POST:
Log relevante:
```

## Dumps recibidos - BIOS Rel. 1.06

Ficheros locales, no versionados:

- `dumps/original/PCS286S_REL.1.06_LOW.BIN`
- `dumps/original/PCS286S_REL.1.06_HIGH.BIN`

Datos observados:

- Tamano de cada chip: 65536 bytes / 64 KiB.
- Tamano de BIOS combinada: 131072 bytes / 128 KiB.
- Orden correcto: `LOW` en direcciones pares, `HIGH` en direcciones impares.
- Candidato correcto: `dumps/derived/candidate_a_low_even.bin`.
- SHA-256 combinado: `88ef6bf52e6c1aea6f7612faef1989702f3a500ee3312ddef5a590b68c63909a`.
- Vector de reset en offset `0x1FFF0`: `EA 5B E0 00 F0`.
- Decodificacion del reset: salto lejano a `F000:E05B`, fisica `0xFE05B`.
- Cadena identificativa: aparece una mencion a Olivetti con ano 1986 en torno al offset `0x1C050`.
