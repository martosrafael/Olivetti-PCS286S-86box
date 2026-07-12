# Publicacion en GitHub

Recomendacion: repositorio privado al principio. Cuando arranque de forma fiable y tengamos claro que no se sube ningun material con copyright, se puede decidir si hacerlo publico.

## Que se sube

- Scripts de analisis.
- Documentacion.
- Notas de hardware.
- Parches contra 86Box.
- Informes con hashes y diagnostico, si no contienen bytes de la BIOS.

## Que no se sube

- Dumps originales de BIOS.
- BIOS combinadas generadas.
- ROM sets de 86Box.
- Ejecutables de 86Box compilados.

## Primer push recomendado

Cuando tengas un repositorio vacio creado en GitHub:

```powershell
git remote add origin https://github.com/TU_USUARIO/olivetti-pcs286s-86box.git
git branch -M main
git push -u origin main
```

Si usas GitHub CLI:

```powershell
gh repo create olivetti-pcs286s-86box --private --source . --remote origin --push
```

