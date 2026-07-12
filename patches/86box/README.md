# Parche 86Box - pendiente

Este directorio queda reservado para el parche real contra 86Box.

Antes de escribirlo necesitamos:

1. Identificar la BIOS combinada correcta.
2. Saber si el cuelgue ocurre antes o despues de inicializar video.
3. Tener un log/traza de puertos o, como minimo, el ultimo texto/codigo POST.

La primera version del parche deberia ser intencionadamente pequena:

- declarar la maquina "Olivetti PCS 286S";
- cargar `roms/machines/olivetti_pcs286s/bios.bin`;
- reutilizar una inicializacion AT 286 existente;
- activar trazas para descubrir que hardware especifico falta.

