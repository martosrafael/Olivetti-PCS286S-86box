# Preservacion del Olivetti PCS 286S

Este proyecto conserva el firmware, los datos de hardware y el trabajo necesario
para emular un Olivetti PCS 286S en 86Box. La maquina de referencia es un 80286 a
16 MHz con coprocesador 80287, VGA Paradise integrada y BIOS Olivetti Release 1.06.

La implementacion actual completa Resident Diagnostics, detecta correctamente los
2048 KB configurados, conserva el CMOS y arranca MS-DOS 6.22.

## Objetivo

No queremos conservar solamente un ejecutable que hoy funciona. Queremos dejar:

- los dumps originales identificados mediante hashes;
- el procedimiento exacto para reconstruir la ROM de 128 KiB;
- los hallazgos sobre el hardware y la BIOS;
- un parche revisable contra 86Box;
- y, finalmente, soporte oficial en 86Box y su repositorio de ROMs.

Los binarios de las ROM no se publican directamente aqui. Se enviaran al
repositorio oficial de ROMs de 86Box cuando el soporte de la maquina haya sido
aceptado, de acuerdo con las normas del proyecto.

## Estado probado

- CPU fijada a 16 MHz y coprocesador 80287 configurado.
- VGA Paradise PVGA1A.
- POST y Resident Diagnostics completos.
- 640 KB de memoria base y 1408 KB extendida con 2048 KB totales.
- Disquetera de 3,5 pulgadas y alta densidad operativa.
- CMOS persistente y coherente con la configuracion de 86Box.
- Arranque e instalacion de MS-DOS 6.22 comprobados.

El mensaje `ROM Checksum Error : 4E` tambien aparece en el ordenador fisico. El
codigo `4E` es un punto de control del POST, no el valor matematico del checksum.
La mitad `E0000-EFFFF` de este dump no suma cero; el envejecimiento de un EPROM es
una explicacion plausible, aunque no se puede demostrar sin otra copia independiente
de la misma BIOS. Los originales deben conservarse sin modificar.

La documentacion principal y los hashes estan en [README.md](README.md).
