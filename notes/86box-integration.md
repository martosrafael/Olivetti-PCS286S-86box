# Integracion con 86Box

## Punto importante

86Box no carga cualquier BIOS arbitraria solo por renombrarla: las rutas y nombres de ROM esperados estan definidos en el emulador. El argumento `--rompath` / `-R` sirve para decir donde esta la raiz del set de ROMs, pero la maquina emulada sigue esperando nombres concretos.

Por eso hay dos fases:

1. Preparar la BIOS combinada correcta desde los dos chips.
2. Anadir una maquina nueva o variante en 86Box que apunte a esa BIOS y reproduzca el hardware que la BIOS espera.

## Flujo recomendado

1. Generar `candidate_a_low_even.bin` y `candidate_b_low_even.bin` con `tools/bios_tool.py`.
2. Elegir el candidato con vector de reset plausible.
3. Crear una rama/fork de 86Box.
4. Empezar desde una maquina AT 286 cercana, no desde cero.
5. Anadir una entrada "Olivetti PCS 286S" con una ruta de ROM dedicada, por ejemplo:

   ```text
   roms/machines/olivetti_pcs286s/bios.bin
   ```

6. Copiar el candidato bueno a esa ruta como `bios.bin`.
7. Compilar 86Box y arrancar una VM minima.
8. Si se queda colgada, instrumentar:

   - codigos POST por puerto 80h si la BIOS los emite;
   - accesos a puertos de teclado/controlador 8042;
   - CMOS/NVRAM;
   - temporizador/PIC/DMA;
   - puertos propietarios Olivetti si aparecen en el desensamblado o en trazas.

## Sospechas tipicas cuando "sale BIOS pero se queda pillada"

- Orden de chips invertido: la CPU ejecuta algo, pero algun salto o tabla queda corrupta.
- Tamano o mapeo de ROM incorrecto: la BIOS espera espejo en F0000-FFFFF o una ventana mayor.
- CMOS/NVRAM no compatible: muchas BIOS AT paran si no leen una configuracion valida.
- Controlador de teclado distinto o comandos no implementados.
- Chipset/memoria: la BIOS prueba registros de chipset que en una placa AT generica no existen.
- Video: si el Olivetti esperaba una configuracion concreta, puede quedar esperando una respuesta que la VGA/CGA elegida no da.

## Parche minimo esperado

El parche final probablemente tocara al menos:

- `src/machine/m_at_286.c` o un nuevo fichero de maquina.
- `src/machine/CMakeLists.txt`.
- `src/machine/machine_table.c`.
- Posiblemente algun dispositivo nuevo si el PCS 286S usa puertos propietarios.

No conviene escribir ese parche "a ciegas" antes de inspeccionar los dumps: podemos acabar emulando una placa AT generica que solo arranca por casualidad.

