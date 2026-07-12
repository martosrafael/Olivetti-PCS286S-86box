# Parches 86Box

Este directorio contiene parches candidatos contra 86Box.

## Parches

- `0001-add-olivetti-pcs286s-machine.patch`: alta minima de la maquina Olivetti PCS 286S contra 86Box actual.
- `0002-wip-olivetti-kbc-post-commands.patch`: extension experimental del KBC Olivetti basada en los logs de la copia antigua.

## Aplicacion local

Desde la raiz de un checkout de 86Box:

```powershell
git apply <ruta-a-este-repo>\patches\86box\0001-add-olivetti-pcs286s-machine.patch
git apply <ruta-a-este-repo>\patches\86box\0002-wip-olivetti-kbc-post-commands.patch
```

Despues coloca los dumps locales, no versionados, en:

```text
roms/machines/olivetti_pcs286s/PCS286S_REL.1.06_LOW.BIN
roms/machines/olivetti_pcs286s/PCS286S_REL.1.06_HIGH.BIN
```

## Siguiente investigacion

La copia antigua que llegaba a arrancar apunta a un bucle de teclado/controlador 8042. Si el parche minimo se vuelve a quedar en el mismo punto, aplica el parche WIP del KBC y compara el ultimo patron de E/S.
