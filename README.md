# Light-curves-Simulations-Vera-Rubin — archivo de insumos SNANA

> **¿Buscas el pipeline?** Está en el repo dedicado
> **[ALCeS](https://github.com/mauriciovalenzuela742/ALCeS)** — código Python,
> instalación, arquitectura de 6 capas, y el panel de estado en vivo
> ([mauriciovalenzuela742.github.io/ALCeS](https://mauriciovalenzuela742.github.io/ALCeS/)).
> Empieza ahí. **Este repo no tiene código ejecutable** — es el archivo de
> insumos curados (configs de modelo, catálogos, scripts originales) que
> ALCeS consume como referencia.

**Autor:** Mauricio Valenzuela C. · Universidad de Chile / ALeRCE
**Infraestructura:** NLHPC (SLURM, Lmod) · SNANA `11.05p`

---

## Qué hay en cada carpeta

| Carpeta | Contenido | README propio |
|---|---|---|
| [`model_config/`](model_config/) | Un `SIMGEN_INCLUDE_<clase>.INPUT` curado por cada una de las ~40 clases de transiente/variable soportadas | [ver](model_config/README.md) |
| [`run_SNANA/`](run_SNANA/) | Recursos compartidos por todo el survey: `KCOR_FILE`, `HOSTLIB`, eficiencia de búsqueda | [ver](run_SNANA/README.md) |
| [`DATASIM_LSST/`](DATASIM_LSST/) | Scripts SLURM + `.INPUT` **manuales** (pre-pipeline) que se corrían uno por uno, un directorio por clase × estrategia | [ver](DATASIM_LSST/README.md) |
| [`SIMLIB/`](SIMLIB/) | Notebooks de análisis de las librerías de cadencia (SIMLIB) | [ver](SIMLIB/README.md) |

**Ninguna de estas carpetas depende de las otras** — cada una es una
colección de archivos de referencia, no un programa. El único lugar donde se
ejecuta algo es en el repo `ALCeS`.

## Relación con ALCeS

`DATASIM_LSST/` documenta el flujo **anterior**: correr `sbatch` a mano por
cada clase, copiando y editando un `.INPUT` a la vez. El pipeline `ALCeS`
reemplaza ese flujo manual — genera esos mismos `.INPUT` automáticamente a
partir de un YAML (`campaigns/*.yaml` + `pipeline/models.yaml` en ese repo),
pero sigue **leyendo** `model_config/` y `run_SNANA/` de este repo como
fuente de los parámetros curados por clase. Es decir: este repo es la
"biblioteca de referencia científica", y `ALCeS` es el orquestador que la usa.

## Referencias

- Kessler+ 2009 — SNANA: A Public Software Package for Supernova Analysis
- Vincenzi+ 2019 — Spectroscopically classified SNe from the Dark Energy Survey
- Ramírez+ 2024 — arXiv:2409.10701 (transporte óptico, modelos VC25)
- Rubin v5.3 release — community.lsst.org/t/release-of-v5-3-simulations/12032
- ALeRCE broker — alerce.science
