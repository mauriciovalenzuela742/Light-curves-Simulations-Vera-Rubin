# Simulaciones de Curvas de Luz — Vera C. Rubin / SNANA

Pipeline config-driven para generar datasets sintéticos de curvas de luz a
partir de las simulaciones de estrategia de observación (OpSim) del
Observatorio Vera C. Rubin, usando SNANA como motor de simulación. Los
datasets alimentan el pipeline de clasificación fotométrica de ALeRCE.

**Autor:** Mauricio Valenzuela C. · Universidad de Chile · ALeRCE
**Infraestructura:** NLHPC (SLURM, Lmod) · SNANA `11.05p`
**Bases verificadas:** `baseline_v5.0.0_10yrs` · `baseline_v5.3.1_10yrs`
(17 bases registradas en total — ver `pipeline/opsims.yaml`)

> Este README refleja el estado **verificado contra la instalación real en
> NLHPC**, no solo contra la documentación genérica de SNANA. Varias rutas,
> nombres de clave y el mecanismo de lanzamiento se corrigieron durante la
> puesta en marcha real — ver la sección "Decisiones y correcciones" al final.

> **¿Primera vez con esto?** Este README es la referencia técnica/arquitectura.
> Para instalar y correr el pipeline de punta a punta sin experiencia previa
> (incluyendo qué corre en el login node vs. qué corre por SLURM, y por qué
> importa), ver **[`INSTALL.md`](INSTALL.md)**.

> **Panel de estado en vivo:** [mauriciovalenzuela742.github.io](https://mauriciovalenzuela742.github.io/)
> — arquitectura por capas, catálogo de las 42 clases, y estado de la última
> campaña compilada. Fuente versionada en [`docs/dashboard/`](docs/dashboard/).

---

## Visión general

El pipeline convierte la cadencia del cielo (bases OpSim) en datasets
clasificables en 6 pasos. Los `.FITS` que produce `snlc_sim.exe` (`HEAD`/`PHOT`)
son la fuente de verdad del dataset — el pipeline no los convierte a otro
formato, solo los usa para generar QC:

```
OpSim .db  →  SIMLIB  →  .INPUT + sbatch  →  snlc_sim.exe  →  FITS  →  QC  →  tags
  Capa 0       Capa 1        Capa 2            Capa 3        Capa 4      Capa 5
```

Agregar una versión nueva de OpSim, una clase de transiente nueva, o repetir
la campaña completa con parámetros distintos es cuestión de editar un YAML y
recompilar — no de tocar scripts sueltos por clase.


## Arquitectura por capas

| Capa | Responsabilidad | CLI | Config |
|------|----------------|-----|--------|
| **0** | Registro y descarga de bases OpSim | `fetch_opsim.py` | `opsims.yaml` |
| **1** | Generación de SIMLIB (WFD/DDF) | `build_simlib.py` | `simlib.yaml` |
| **2** | Compilación de `.INPUT` + scripts SLURM | `compile_campaign.py` | `campaign.yaml` + `models.yaml` |
| **3** | Validación pre-vuelo + lanzamiento (`sbatch` por clase) | `run_campaign.py` | (usa la Capa 2) |
| **4** | QC directo sobre los FITS (sin conversión a tablas) | `postprocess.py` | — |
| **5** | Procedencia y reproducibilidad | `tag_campaign.py` | — |

**Guardias anti-login-node.** Las Capas 1 y 4 (`build_simlib` contra un `.db`
real, y `postprocess --campaign`) son cómputo pesado y se niegan a correr
fuera de un job SLURM — detectan `$SLURM_JOB_ID` y abortan con el comando
`sbatch` correcto si no está presente. Detalle en "Flujo completo de
ejecución" y en `INSTALL.md`.


## Qué hay en este repo vs. qué corre en NLHPC

> **Este repositorio de GitHub contiene los insumos curados que el pipeline
> consume** (`model_config/`, `run_SNANA/`, `DATASIM_LSST/`, `SIMLIB/` — los
> `SIMGEN_INCLUDE_*.INPUT`, `KCOR_FILE`, `HOSTLIB`, y los scripts manuales
> originales que el pipeline reemplazó). **El código Python del pipeline en
> sí** (`pipeline/`, `campaigns/`, `slurm/`, todo lo que describe el árbol de
> abajo como `AUTOSIM/`) **vive únicamente en `~/AUTOSIM` dentro de NLHPC**
> — todavía no está sincronizado a este repo de GitHub. La estructura de
> abajo documenta el layout real en NLHPC para quien tenga acceso al
> cluster, no lo que vas a encontrar navegando este repo en el navegador.

## Estructura del repositorio (deployment real en NLHPC, `~/AUTOSIM`)

```
AUTOSIM/
├── pipeline/
│   ├── __init__.py · paths.py · registry.py · fetch_opsim.py      ← Capa 0
│   ├── opsims.yaml            (registro curado, 17 bases)
│   ├── opsims.local.yaml      (auto-gestionado: checksums; gitignored)
│   │
│   ├── simlib/                ← Capa 1: constructor de SIMLIB
│   │   ├── classify.py        (aislamiento de esquema OpSim v5.0/v5.3)
│   │   ├── formatobs.py, coverage.py, writer.py, hprep.py, config.py, timeutil.py
│   ├── build_simlib.py
│   ├── simlib.yaml
│   │
│   ├── campaign/               ← Capa 2: compilador de .INPUT + SLURM
│   │   ├── compiler.py         (expande campaign.yaml → .INPUT + sbatch)
│   │   └── templates.py        (claves REALES de sim-input SNANA, ver abajo)
│   ├── compile_campaign.py
│   ├── models.yaml              (42 clases, rutas reales verificadas en NLHPC)
│   │
│   ├── orchestrate/            ← Capa 3: preflight + lanzamiento + monitoreo
│   │   ├── preflight.py, launcher.py, monitor.py
│   ├── run_campaign.py
│   │
│   ├── postproc/                ← Capa 4: QC (lee FITS en memoria, no escribe tablas)
│   │   ├── converter.py, qc.py
│   ├── postprocess.py
│   │
│   ├── provenance/              ← Capa 5: procedencia
│   │   ├── tagger.py, environment.py
│   └── tag_campaign.py
│
├── campaigns/
│   ├── test_small.yaml         (2 clases, NGEN chico — validación end-to-end)
│   └── full_v5.3.yaml          (42 clases × WFD+DDF — campaña real)
├── data/opsim/                 (bases .db descargadas; gitignored)
├── data/simlib/                (SIMLIB generados por Capa 1; gitignored)
├── slurm/
│   ├── build_simlib.sbatch     (Capa 1 completa, sin --limit, vía SLURM)
│   └── run_pipeline_step.sbatch (wrapper generico para pasos pesados)
├── build/                      (salida de compile_campaign; gitignored)
├── tests/test_simlib_core.py
├── setup_autosim.py            (reorganizador + auto-reparador)
└── activate_all.sh              (venv + módulo SNANA + env vars en un comando)
```


## Entorno real en NLHPC

**Cada sesión nueva, un solo comando:**

```bash
cd ~/AUTOSIM
source activate_all.sh
```

`activate_all.sh` busca el venv automáticamente (no asumas que está en
`AUTOSIM/venv/` — en este entorno terminó en `AUTOSIM/pipeline/venv/`; el
script lo detecta solo en ambas ubicaciones, o lo busca en todo `AUTOSIM` si
no lo encuentra ahí), carga `module load SNANA/11.05p`, exporta
`$SNDATA_ROOT`, y termina con una verificación (`which snlc_sim.exe`).

Si prefieres hacerlo a mano:

```bash
source pipeline/venv/bin/activate      # OJO: no "venv/bin/activate" a secas
module load SNANA/11.05p               # mayúsculas — Lmod es case-sensitive
export SNDATA_ROOT=/home/mvalenzuela/SNDATA_ROOT
```

**Dependencias del venv** (además de `pipeline/requirements.txt`):

```bash
pip install 'numpy>=2,<2.4' healpy astropy fitsio rubin-sim
git clone https://github.com/LSSTDESC/OpSimSummaryV2.git ~/OpSimSummaryV2
pip install ~/OpSimSummaryV2
```

(`pyarrow` no se necesita — la Capa 4 no escribe Parquet, ver "Decisiones y
correcciones", ítem 12. El pin `numpy<2.4` evita una regresión conocida de
NumPy 2.4.x que causa `Illegal instruction` al importar en ciertas CPUs —
ver ítem 13, aunque la causa real en NLHPC era otra (el intérprete de
Python, no numpy). El venv en si debe crearse con
`module load python/3.12.3-legacy-skylake`, no el módulo Python por
defecto — ver `INSTALL.md` sección 3 e ítem 13 más abajo.)

`healpy` sí instala vía wheel precompilado en Linux x86-64 (no así en
Windows — por eso la Capa 1 contra un `.db` real solo corre en NLHPC, no en
tu máquina local). `opsimsummaryv2` no está en PyPI, se instala desde GitHub.

**Verificación rápida del entorno:**

```bash
which snlc_sim.exe        # debe apuntar a $SNANA_DIR/bin/snlc_sim.exe
echo $SNDATA_ROOT          # debe ser /home/mvalenzuela/SNDATA_ROOT
python -c "import healpy, opsimsummaryv2, rubin_sim; print('OK')"
```


## Instalación / reorganización

Si reorganizas archivos sueltos con `setup_autosim.py` (por ejemplo tras
copiar cada capa a mano en carpetas `Capa0/`…`Capa5/`):

```bash
python setup_autosim.py
```

Reescribe los 6 `__init__.py` y los 4 YAML de configuración con su contenido
correcto (por si se copiaron mal), verifica que los `.py` de lógica estén
presentes, y corre los self-tests de las 5 capas. Es seguro correrlo varias
veces — no toca tu código de lógica si ya existe.

**Nota Windows:** usa `python`, no `python3` (en Windows el segundo suele no
existir o abre la Microsoft Store).


## Flujo completo de ejecución

**Política: cómputo real → SLURM. Orquestación/IO liviano → login node.**
No es "todo por SLURM" a ciegas — es que cada paso vaya donde corresponde:

| Paso | Dónde | Por qué |
|---|---|---|
| `fetch_opsim` (Capa 0) | login node | descarga de red, no cómputo |
| `build_simlib` (Capa 1) | **SLURM** (`slurm/build_simlib.sbatch`) | Healpix + BallTree sobre ~1.8M filas |
| `compile_campaign` (Capa 2) | login node | solo escribe texto, milisegundos |
| `run_campaign --launch` (Capa 3) | login node | solo hace `sbatch` por cada script — el cómputo real (`snlc_sim.exe`) corre en los jobs que dispara, no en el login node |
| `run_campaign --status` | login node | solo lee logs + `squeue` |
| `postprocess` (Capa 4) | **SLURM** si son muchas clases (`slurm/run_pipeline_step.sbatch`); login node si son 2-3 | lectura de FITS grandes + matplotlib puede ser pesado |
| `tag_campaign` (Capa 5) | login node | solo hashea archivos ya generados |

Los dos scripts en `slurm/` (`build_simlib.sbatch`, `run_pipeline_step.sbatch`)
activan el entorno con `source activate_all.sh` — **nunca** hardcodean
`venv/bin/activate` (ese bug rompió silenciosamente corridas completas de
`build_simlib` antes de detectarlo — ver "Decisiones y correcciones").

**Esta política ya no depende solo de que la sigas de memoria.** `build_simlib`
contra un `.db` real y `postprocess --campaign` chequean `$SLURM_JOB_ID` al
arrancar (SLURM lo exporta siempre dentro de un job `sbatch`/`srun`) y se
niegan a correr si no está — muestran el `sbatch` correcto y abortan. El
escape manual para los casos que esta misma tabla marca como aceptables en
login (p.ej. `postprocess` con 2-3 clases) es `--allow-login`, que además
imprime una advertencia — es la excepción documentada, no una forma de
ignorar la política. `build_simlib --self-test` y `postprocess --self-test`
son sintéticos/livianos y nunca piden el guardia.

### Paso 1 — Registrar y descargar la base OpSim (Capa 0)

```bash
python -m pipeline.fetch_opsim --list
python -m pipeline.fetch_opsim --run baseline_v5.3.1_10yrs
```

Usa `--skip-existing` para no re-verificar (recalcular sha256) bases ya
descargadas. En NLHPC, redirige el destino a scratch si quieres:
`export RUBIN_OPSIM_DIR=/scratch/$USER/opsim`.

### Paso 2 — Generar los SIMLIB (Capa 1) — **vía SLURM**

Esto sí es cómputo pesado (Healpix + BallTree sobre ~1.8M observaciones):
nunca correrlo en el login node.

```bash
mkdir -p logs
sbatch slurm/build_simlib.sbatch baseline_v5.3.1_10yrs WFD
sbatch slurm/build_simlib.sbatch baseline_v5.3.1_10yrs DDF
squeue -u $USER
```

El script pide la partición `largemem` explícita (NLHPC reasigna ahí
automáticamente jobs con esta razón memoria/CPU; pedirla directo evita el
aviso de reasignación). Revisa `logs/build_simlib_*.out` cuando terminen.

> **Verifica que de verdad terminaron.** Antes de la corrección del bug del
> venv (ver "Decisiones y correcciones", ítem 10), estos jobs fallaban en
> silencio en la línea de activación del entorno — el `.err` mostraba
> `venv/bin/activate: No such file or directory` y nada más corría después.
> Si tu SIMLIB actual (`data/simlib/<run>/*.SIMLIB`) es de menos de ~1 MB o
> viene de una corrida con `--limit`, probablemente es el de prueba, no el
> real — vuelve a correr estos dos `sbatch` con el script ya corregido antes
> de lanzar la campaña completa.

### Paso 3 — Compilar la campaña (Capa 2) — **login node, es liviano**

```bash
python -m pipeline.compile_campaign --config campaigns/test_small.yaml
```

Genera en `build/<nombre>/`:
- `includes/include_survey_{WFD,DDF}_<run>.INPUT` — cadencia, SIMLIB, SEARCHEFF,
  KCOR, filtros, `SIMGEN_DUMPALL` (todo lo que es igual para cualquier clase)
- `includes/include_model_<clase>.INPUT` — un passthrough de una línea
  (`INPUT_INCLUDE_FILE:`) a tu `SIMGEN_INCLUDE_*.INPUT` ya curado
- `sim_<clase>_<estrategia>_<run>.INPUT` — el archivo raíz que SNANA ejecuta
- `slurm/run_<GENVERSION>.sh` — **un script `sbatch` por clase**, que llama
  `snlc_sim.exe sim_<GENVERSION>.INPUT` directo (ver "Cómo se lanza" abajo)
- `submit_all.sh` — lanza todos los `sbatch` de la campaña de una vez
- `campaign_manifest.json` — inventario de todo lo anterior

### Paso 4 — Validar y lanzar (Capa 3)

```bash
# Solo validar (7 checks: snlc_sim.exe, SNDATA_ROOT, SIMLIBs, modelos, SLURM…):
python -m pipeline.run_campaign --launch campaigns/test_small.yaml --dry-run

# Validar + lanzar de verdad (un sbatch por GENVERSION):
python -m pipeline.run_campaign --launch campaigns/test_small.yaml
```

**Monitoreo y verificación**, en orden:

```bash
# 1. ¿Sigue en cola o ya terminó?
squeue -u $USER

# 2. Resumen por GENVERSION (lee logs + $SNDATA_ROOT/SIM/)
python -m pipeline.run_campaign --status build/test_small

# 3. Logs crudos: caen en build/<campaña>/ (NO en slurm/), porque sbatch
#    corre con cwd = build_dir. Nombre: run_<GENVERSION>_<jobid>.{out,err}
ls build/test_small/*.out build/test_small/*.err
grep -i "DONE EVERYTHING\|ABORT\|FATAL" build/test_small/*.out

# 4. Confirmar que los FITS realmente se generaron
ls $SNDATA_ROOT/SIM/SNIa_WFD_baseline_v5.3.1_10yrs/
ls $SNDATA_ROOT/SIM/SNII_WFD_baseline_v5.3.1_10yrs/
```

Si el paso 3 muestra `DONE EVERYTHING` para cada GENVERSION y el paso 4
lista `PHOT.FITS.gz`/`HEAD.FITS.gz`, la campaña terminó bien → seguir al
Paso 5.

### Paso 5 — Post-proceso (Capa 4)

Cuando los jobs terminen (confirmar con `--status` o `squeue`), lee los FITS
en memoria y genera los 4 QC — no convierte a CSV/Parquet, los `.FITS` ya son
el dataset final. Para campañas con muchas clases esto es pesado y el
guardia lo bloquea sin SLURM — usa `slurm/run_pipeline_step.sbatch`:

```bash
# liviano (pocas clases, ej. test_small — excepcion documentada, requiere --allow-login):
python -m pipeline.postprocess --campaign build/test_small --allow-login

# pesado (campaña completa, vía SLURM — la forma normal):
sbatch slurm/run_pipeline_step.sbatch pipeline.postprocess --campaign build/full_v5.3
```

Genera por GENVERSION: `postproc/<gv>/qc/*_qc_{redshift,magnitudes,detections,lightcurves}.png`
+ `postprocess_manifest.json` consolidado.

### Paso 6 — Etiquetar procedencia (Capa 5)

```bash
python -m pipeline.tag_campaign --campaign build/test_small
```

Genera un `.provenance.json` por GENVERSION (versión OpSim, versión SNANA,
hash de configs, timestamps, inventario I/O, snapshot del entorno) y un
`PROVENANCE_MANIFEST.json` consolidado.

### Paso 7 — Escalar a la campaña completa

Una vez que `test_small` corrió de punta a punta sin errores (simulación →
QC → tags), repite exactamente los pasos 3–6 con
`campaigns/full_v5.3.yaml` (42 clases × WFD + DDF = 84 GENVERSION).


## Receta rápida: agregar una base OpSim nueva y lanzar la campaña completa

Pensada para ejecutarse de punta a punta con una sola instrucción a Claude
(p.ej. *"agrega la base `baseline_v5.3.2_10yrs` y lanza la campaña completa
para las 42 clases"*). Asume entorno ya instalado (`INSTALL.md`) y conexión
SSH ya configurada.

1. **Verificar/registrar la base en `pipeline/opsims.yaml`.** La mayoría de
   las bases `baseline_*`/`roll_*`/`ddf_*` de la release 5.3 ya están
   registradas con `status: registered` (no descargadas todavía) — confirmar
   con `python -m pipeline.fetch_opsim --list`. Si no está, agregar una
   entrada nueva (`release`, `family`, `filename` — copiar el patrón de una
   entrada existente de la misma familia; el `filename` real hay que
   confirmarlo contra el índice S3DF, no solo contra anuncios — ver
   "Decisiones y correcciones", ítem 7).

2. **Descargar (Capa 0, login node):**
   ```bash
   python -m pipeline.fetch_opsim --run <NUEVA_BASE>
   ```

3. **Generar SIMLIB para ambas estrategias (Capa 1, SLURM, obligatorio):**
   ```bash
   mkdir -p logs
   sbatch slurm/build_simlib.sbatch <NUEVA_BASE> WFD
   sbatch slurm/build_simlib.sbatch <NUEVA_BASE> DDF
   squeue -u $USER   # esperar a que ambos desaparezcan
   ```
   Confirmar cobertura real de 10 años (o los que corresponda) en el `.out`:
   línea `cobertura: ... (X.XX a)`. Si `pipeline/simlib.yaml` tiene un
   `temporal_cut` con `date_max` no-nulo, el SIMLIB queda recortado aunque
   el nombre de la base diga "10yrs" — confirmar que `temporal_cut.date_min`
   y `date_max` sean `null` (survey completo) antes de generar, salvo que el
   recorte sea intencional.

4. **Crear/adaptar el campaign YAML.** Si ya existe uno para la misma
   combinación de clases (p.ej. `campaigns/full_v5.3.yaml`), copiarlo y
   cambiar `runs: - run: <NUEVA_BASE>` y el campo `name:` para que incluya
   una señal identificable de la base/rango usado (p.ej. `full_v5.3.2_10yrs`)
   — así el `build_dir` (`build/<name>/`) nunca colisiona con una
   compilación anterior de otra base o de un rango temporal distinto.

5. **Compilar + preflight + lanzar (Capas 2–3):**
   ```bash
   python -m pipeline.compile_campaign --config campaigns/<nueva>.yaml
   python -m pipeline.run_campaign --launch build/<nombre_campaña> --dry-run   # confirmar "pre-flight OK"
   python -m pipeline.run_campaign --launch build/<nombre_campaña>            # lanza los sbatch reales
   ```
   Si el preflight marca `modelo <X>: no encontrado`, es un problema de
   `models.yaml` (ruta rota o cuenta distinta — ver `INSTALL.md` sección
   2.5), no de la base OpSim nueva — resolver antes de lanzar.

6. **Monitorear y validar** con `--status`, luego Capa 4 (`postprocess`,
   vía `sbatch slurm/run_pipeline_step.sbatch` si son muchas clases) y Capa
   5 (`tag_campaign`) — igual que en el flujo de `test_small` más arriba.

Con esto, agregar una base nueva es una operación mecánica de ~6 comandos
sin decisiones de diseño pendientes — el único paso no automatizable es
confirmar el `filename` real en el índice S3DF si la base no está ya
registrada en `opsims.yaml`.


## Cómo se lanza cada simulación (importante)

**No se usa `submit_batch_jobs.sh`.** Se probó documentado en el manual de
SNANA, pero requiere un archivo de plantilla SLURM (`BATCH_INFO: sbatch
<template> <n_core>`) que no existe en esta instalación, y su formato real
(`CONFIG:`/`GENVERSION_LIST:` como YAML, `SIMGEN_INFILE_SNIa/NONIa`) es
distinto al de un `.INPUT` de SNANA genérico — costó varias iteraciones
descubrirlo. En cambio, el pipeline replica **el patrón que ya usabas con
éxito** en `DATASIM_LSST/*/input_files_v6/<clase>/run_<clase>_<fecha>.sh`:

```bash
#!/bin/bash
#SBATCH -p general
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem-per-cpu=2000
ml SNANA/11.05p
export SNDATA_ROOT=/home/mvalenzuela/SNDATA_ROOT
snlc_sim.exe sim_<GENVERSION>.INPUT
```

Un `sbatch` de estos por GENVERSION, generado automáticamente por la Capa 2.
`run_campaign.py --launch` los envía todos y guarda los job IDs reales
(capturados de la salida de `sbatch`) en `launch.json`.


## Catálogo de modelos (`models.yaml`)

Cada clase referencia un `SIMGEN_INCLUDE_*.INPUT` **ya curado** en tu
instalación real (no reinventamos `DNDZ`, pesos por plantilla `NON1A:`, ni
rangos — eso ya está afinado por el autor original):

```yaml
SNIa:
  simgen_include: "/home/mvalenzuela/run_SNANA/model_config/SIMGEN_INCLUDE_SNIa-SALT2.INPUT"
  ngen: 50000
```

El compilador genera un passthrough de una línea:
`INPUT_INCLUDE_FILE:  <ruta>`.

Tres ubicaciones reales de `SIMGEN_INCLUDE`:

| Ubicación | Contenido |
|---|---|
| `~/run_SNANA/model_config/` | 34 archivos canónicos (PLAsTiCC + ELASTiCC + `VC25_SNIbc`) |
| `~/run_SNANA/elastic/model_config/` | 4 variantes NON1ASED "en desarrollo" |
| `~/OTMODEL_NON1ASED/SNtypes/` | Tus modelos VC25 (transporte óptico, Ramírez+2024) |

**42 clases en total:** 21 PLAsTiCC (incluye las 3 variantes de `uLens` y
las 3 de `PISN` — no se elige una sola), 10 ELASTiCC (Vincenzi+2019), 5
NON1ASED en desarrollo, y 2 VC25 propios (`VC25_SNIbc`, `VC25_SNII`).

### Agregar una clase nueva

```yaml
MiClaseNueva:
  simgen_include: "/ruta/absoluta/SIMGEN_INCLUDE_MiClaseNueva.INPUT"
  ngen: 10000    # NGENTOT_LC — ver nota abajo
```

Y agregarla a la lista `classes:` del `campaign.yaml` correspondiente.


## `NGENTOT_LC` por clase y estrategia

**Ya calibrado con tus valores reales** (extraídos de
`DATASIM_LSST/{WFD,DDF}/input_files_v6/*/*.input` en el repo). El valor
correcto **depende de la estrategia**, no solo de la clase — DDF tiene
muchos menos campos que WFD, así que su `NGENTOT_LC` es típicamente ~100×
menor:

```yaml
SNIa:
  ngen_wfd: 200000   # NGENTOT_LC real (DATASIM_LSST/WFD)
  ngen_ddf: 2000      # NGENTOT_LC real (DATASIM_LSST/DDF)
```

`compiler.py` resuelve el valor con esta prioridad: override explícito en
`campaign.yaml` (`- model: X / ngen: N`) > `ngen_wfd`/`ngen_ddf` real de
`models.yaml` según la estrategia que se está compilando > `ngen` genérico
de respaldo.

**40 de 42 clases** tienen valores reales. Quedan pendientes de calibrar
(sin `.input` real en el repo todavía, usan un placeholder `10000` marcado
`SIN CALIBRAR`):
- `SNIax_NON1ASED`
- `TDE_NON1ASED`

Y 4 clases con dato real solo de un lado (el otro queda estimado, marcado
`# ESTIMADO` en `models.yaml`): `SLSN-I_NON1ASED` y `SNIa-91bg_NON1ASED`
(falta DDF), `VC25_SNII` y `VC25_SNIbc` (falta WFD).

Para agregar el valor real de una clase nueva o corregir un placeholder:

```bash
grep NGENTOT_LC /ruta/a/tu/archivo_real.input
# y editar ngen_wfd:/ngen_ddf: en pipeline/models.yaml
```


## Notas técnicas

**Aislamiento de esquema OpSim.** La clasificación `scheduler_note` →
`field_type` (WFD/DDF/twilight/Other) usa prefijos configurables en
`simlib.yaml`, no listas fijas — cubre v5.0 y v5.3 con la misma regla.

**Doble verificación de descarga.** `fetch_opsim.py` chequea tamaño de
archivo (`size_bytes`, contra el índice S3DF real) y sha256 en cada
descarga.

**Reglas SLURM del cluster.** NLHPC reasigna automáticamente a la partición
`largemem` los jobs cuya razón memoria/CPU calza mejor ahí (p.ej. 16 GB / 4
cores). Pedirla explícita evita el aviso de reasignación —
`slurm/build_simlib.sbatch` y `run_pipeline_step.sbatch` ya la piden así.

**QC con identidad visual LSST.** Los gráficos usan el tema nocturno de
observatorio con los colores de los 6 filtros (u/g/r/i/z/Y).


## Decisiones y correcciones durante la puesta en marcha real

Documentado porque cada una costó tiempo real de debugging — sirve como
referencia si algo similar vuelve a fallar:

1. **`PATH_SNDATA_SIM` no es la clave de rutas de modelo NON1ASED** — es
   `PATH_NON1ASED`. (`PATH_SNDATA_SIM` sí es una clave real de SNANA, pero
   define dónde se escribe el *output*, no las plantillas de entrada.)
2. **`INPUT_FILE_INCLUDE` no existe** — la clave real es `INPUT_INCLUDE_FILE`
   (orden invertido).
3. **`NGEN_LC` vs `NGENTOT_LC`** — semánticas distintas; los `.input` reales
   usan `NGENTOT_LC` (total simulado, no el que pasa cortes).
4. **`submit_batch_jobs.sh` nunca se usó en la práctica** — su formato real
   difiere bastante de lo documentado en el manual genérico, y requiere un
   archivo de plantilla SLURM que no existe en esta instalación. Se
   reemplazó por sbatch directo por GENVERSION, replicando el patrón ya
   probado en `DATASIM_LSST`.
5. **El módulo de NLHPC es `SNANA/11.05p`** (mayúsculas — Lmod es
   case-sensitive) y solo trae los binarios compilados (`bin/`) — los
   scripts de utilidad (`util/`) requieren clonar el repo fuente aparte.
6. **`submit_batch_jobs.sh` exige el nombre pelado del archivo** (sin ruta),
   ejecutado con `cwd` en el mismo directorio — relevante si en el futuro
   se retoma esa vía.
7. **Nombres de archivo del foro vs. el índice real de S3DF pueden diferir**
   (`baseline_v5.3.0_11years.db` en el texto del post vs.
   `baseline_v5.3.0_11yrs.db` real) — siempre confirmar contra el índice,
   no solo contra anuncios.
8. **El venv no vive en `AUTOSIM/venv/`** sino en `AUTOSIM/pipeline/venv/`
   — usar `activate_all.sh`, que lo detecta solo, en vez de asumir la ruta.
9. **`TDE_NON1ASED` / `SNIax_NON1ASED`**: los `SIMGEN_INCLUDE_*_NON1ASED.INPUT`
   (en `elastic/model_config/`) son internamente consistentes —
   `PATH_NON1ASED` apunta a directorios confirmados en
   `elastic/model_libs_updates/` — y `models.yaml` ya referencia esos
   archivos correctamente. Si en NLHPC se observa un problema de ruteo real
   (más allá de lo que el contenido del archivo revela), falta diagnosticar
   directamente en el filesystem — no es un bug conocido del pipeline.
10. **`slurm/build_simlib.sbatch` y `run_pipeline_step.sbatch` tenían el
    mismo bug de ruta del venv** que las sesiones interactivas
    (`source venv/bin/activate` asumiendo raíz de `AUTOSIM`) — pero como es
    un script no interactivo, el error quedaba solo en el `.err` y el job
    terminaba "exitosamente" (exit code de un script que falla en la línea
    de activación pero no usa `set -e` de forma que aborte visible... en
    este caso sí tenía `set -euo pipefail`, así que el job SÍ terminaba con
    error, pero podía pasar desapercibido si no se revisaba el `.err`). Las
    corridas completas de `build_simlib` vía `sbatch` **nunca llegaron a
    ejecutar nada** antes de esta corrección — solo los SIMLIB generados
    interactivamente (p.ej. con `--limit`) existían. Corregido: ambos
    scripts ahora usan `source activate_all.sh`.
11. **`monitor.py` reportaba `RUNNING` por defecto** cuando un log existía
    pero no tenía `ABORT`/`FATAL` — incluso con el job ya fuera de `squeue`
    y sin FITS de salida. Corregido: ese caso ambiguo ahora se reporta como
    `UNKNOWN` con un mensaje explícito, en vez de asumir que sigue
    corriendo.
12. **NLHPC advirtió por correr cómputo pesado en el login node** (antes de
    que existieran los guardias de esta sección). La causa raíz no era falta
    de documentación — la tabla de "Flujo completo de ejecución" ya
    distinguía login vs. SLURM — sino que nada impedía en la práctica saltarse
    esa tabla. Corregido en dos frentes: (a) `build_simlib` (contra un `.db`
    real) y `postprocess --campaign` ahora chequean `$SLURM_JOB_ID` y abortan
    si no están dentro de un job SLURM, mostrando el `sbatch` correcto —
    `pipeline.paths.require_slurm()`; (b) la Capa 4 dejó de escribir
    CSV/Parquet (`postproc/<gv>/tables/`) — los `.FITS` de `snlc_sim` ya eran
    la fuente de verdad y la conversión solo agregaba trabajo (y riesgo de
    correrlo en login) sin necesidad real. `pyarrow` ya no es una dependencia
    del proyecto.
13. **El venv crasheaba con `Illegal instruction (core dumped)` en `general`/
    `largemem`** (jobs 9680064/9680065, nunca resuelto en su momento — el
    `data/simlib/*.SIMLIB` que quedó de esa época era un remanente pequeño,
    no la corrida real). Causa: `pipeline/venv` se creó con el modulo Python
    por defecto de NLHPC (`python/3.11.7-zen4-b`, Spack `linux-rocky9-zen4`),
    compilado para las instrucciones AVX512 del login node (AMD EPYC 9224,
    Zen4). Los nodos `general`/`largemem` (Intel Xeon Gold 6152, Skylake-SP)
    no las soportan — el interprete de Python en si crashea al arrancar,
    antes de llegar a importar numpy. No es un problema de version de numpy
    (se probo con 1.26.4 y 2.3.5, crashea igual) ni de `NPY_DISABLE_CPU_FEATURES`.
    Corregido: recrear el venv con `module load python/3.12.3-legacy-skylake`
    (NLHPC tiene builds `-legacy-skylake` especificos para esto en
    `NLHPC-custom`). `activate_all.sh` ahora carga ese modulo primero (el
    interprete del venv depende en runtime de sus libs, p.ej. `libiomp5.so`).
    Si en el futuro se corre en un nodo Zen4 (partición `main`), este mismo
    venv funciona igual — Skylake es baseline compatible hacia arriba.
14. **Capa 4 (QC) fallaba con `'FLT'` contra FITS reales** — `snlc_sim.exe`
    11.05p nombra la columna de banda `BAND` en el PHOT.FITS, no `FLT` (el
    nombre que asumia `postproc/qc.py`, y que solo se habia probado contra
    datos sinteticos del self-test). Tampoco existe una columna `MAG` cruda
    (solo `FLUXCAL`+`ZEROPT`). Corregido en `postproc/converter.py::read_phot`:
    renombra `BAND`→`FLT` y calcula `MAG`/`MAGERR` desde `FLUXCAL`/`ZEROPT`
    al leer, para no tocar `qc.py`. De paso goles: los FITS vienen en
    big-endian (estandar FITS) y numpy/matplotlib en esta plataforma
    necesitan nativo — sin bytesswap fallaba con "Big-endian buffer not
    supported on little-endian compiler"; ahora `_read_fits_table` normaliza
    el byte order de cada columna al leer.


## Clases de transientes incluidas (42)

**PLAsTiCC (21):** SNIa, SNIa-91bg, SNIax, SNII, SNII-NMF, SNIIn-MOSFIT,
SNIb, SNIc, SLSN-I, TDE, KN-K17, KN-BULLA19, AGN, RRL, Mira, M-dwarf, EB,
ILOT, CaRT, + 3 uLens + 3 PISN.

**ELASTiCC / Vincenzi+2019 (10):** V19_SNIb, V19_SNIc, V19_SNIcBL,
V19_SNII, V19_SNIIb, V19_SNIIn, Cepheid, d-Scuti, Dwarf_nova, Mdwarf-flare.

**NON1ASED en desarrollo (5):** SNIax_NON1ASED, SNIa-91bg_NON1ASED,
TDE_NON1ASED, SLSN-I_NON1ASED, KN-BULLA-BNS-M2COMP.

**VC25 — modelos propios (2):** VC25_SNIbc, VC25_SNII (transporte óptico,
Ramírez+2024).


## Referencias

- Kessler+ 2009 — SNANA: A Public Software Package for Supernova Analysis
- Vincenzi+ 2019 — Spectroscopically classified SNe from the Dark Energy Survey
- Ramírez+ 2024 — arXiv:2409.10701 (transporte óptico, modelos VC25)
- Rubin v5.3 release — community.lsst.org/t/release-of-v5-3-simulations/12032
- ALeRCE broker — alerce.science
- Repo: github.com/mauriciovalenzuela742/Light-curves-Simulations-Vera-Rubin
