# INSTALL.md — instalación y primera corrida en una cuenta NLHPC nueva

Guía de instalación paso a paso para una cuenta NLHPC en la que el pipeline
nunca se ha corrido. Referencia técnica de arquitectura/capas/catálogo de
modelos: [`README.md`](README.md). Esta guía cubre solo instalación +
validación end-to-end.

Sigue las secciones en orden — cada una depende de que la verificación de la
anterior haya pasado. Pensada para ejecutarse también vía Claude Code: cada
bloque de comandos es copiable/pegable tal cual, y las secciones 0 y 2.5
documentan explícitamente qué es específico de la cuenta `mvalenzuela` y qué
hay que adaptar en una cuenta distinta (ver sección 2.5 si estás instalando
para otro usuario, p.ej. un colaborador o supervisor).


## 0. Antes de empezar: dos conceptos que evitan un reto de NLHPC

Esto no es opcional — ya pasó una vez con este proyecto: alguien corrió
cómputo pesado directo en la terminal y NLHPC advirtió por abuso del login
node. El pipeline ahora se niega a repetirlo (ver sección 5), pero entender
**por qué** te va a ahorrar sustos.

**Login node vs. compute node.** Cuando te conectas a NLHPC por SSH, caes en
una máquina compartida por *todos* los usuarios del cluster al mismo tiempo
— el "login node". Sirve para cosas livianas: navegar carpetas, editar
archivos, lanzar trabajos. Si ahí mismo corres algo que usa mucha memoria o
CPU por minutos u horas, se lo estás quitando a todos los demás usuarios
conectados en ese momento — por eso los administradores lo vigilan y
advierten/banean a quien lo hace.

**SLURM y los "jobs".** El cómputo real no se corre a mano — se *encola* con
el comando `sbatch archivo.sbatch`, que le pide a SLURM (el gestor de colas
del cluster) que lo ejecute en una de las máquinas de cómputo dedicadas
("compute nodes"), cuando haya un cupo libre. Tú sigues en el login node,
pero el trabajo pesado corre en otra máquina. Se monitorea con
`squeue -u $USER` y dos comandos más que se explican en la sección 7.

**La regla de este proyecto, en una frase:** si un paso puede tardar más de
unos segundos o usar más de un par de cientos de MB de RAM, va con `sbatch`,
nunca corriéndolo directo. La sección 5 (Capas 1 y 4) lo explica caso por
caso, y el propio código te va a detener si te equivocas.


## 1. Acceso a NLHPC

Si todavía no tienes cuenta, pídela a quien administra el proyecto —
usualmente es una solicitud a través de la web de NLHPC con tu correo
institucional. Con la cuenta activa, conéctate por SSH:

```bash
ssh <tu_usuario>@<host-de-nlhpc>
```

(el host y las credenciales te los da NLHPC al aprobar la cuenta — no están
en este repo). Si esto funciona y ves un prompt, estás en el login node.


## 2. Clonar el repositorio

```bash
cd ~
git clone https://github.com/mauriciovalenzuela742/Light-curves-Simulations-Vera-Rubin.git AUTOSIM
cd AUTOSIM
```

(usa el nombre de carpeta que prefieras; el resto de esta guía asume
`~/AUTOSIM`, que es lo que espera `activate_all.sh`).


## 2.5 Portabilidad entre cuentas NLHPC — leer antes de instalar para otro usuario

Si estás instalando esto en una cuenta NLHPC **distinta** de `mvalenzuela`
(p.ej. la de tu supervisor/colaborador), dos cosas del repo son
account-specific y no funcionan tal cual:

1. **`pipeline/models.yaml`** — cada una de las 42 clases apunta a un
   `simgen_include:` con ruta absoluta bajo `/home/mvalenzuela/...`
   (`run_SNANA/model_config/`, `run_SNANA/elastic/model_config/`,
   `OTMODEL_NON1ASED/SNtypes/`). Son archivos `SIMGEN_INCLUDE_*.INPUT`
   curados manualmente contra el manual de SNANA — no los genera este
   pipeline. En una cuenta nueva **no existen** salvo que:
   - la cuenta nueva tenga permiso de lectura sobre el `$HOME` de
     `mvalenzuela` (poco común por defecto en NLHPC — hay que pedirlo), o
   - copies ese árbol de archivos a la cuenta nueva y edites `models.yaml`
     para apuntar a la nueva ruta base, o
   - ambas cuentas compartan un directorio de proyecto/grupo en NLHPC y
     ahí vivan los `SIMGEN_INCLUDE_*`.

   El `preflight` (sección 8.4) revisa la existencia de cada uno de estos
   archivos antes de lanzar — si faltan, lo dice explícitamente por clase
   (`modelo <X>: no encontrado: <ruta>`), no falla en silencio.

2. **`campaigns/*.yaml` → `defaults:`** — `kcor_file`,
   `searcheff_pipeline_file`, `searcheff_pipeline_logic_file` también son
   rutas absolutas bajo `/home/mvalenzuela/run_SNANA/`. Mismo problema,
   misma solución (compartir o copiar + editar el YAML).

3. **`export SNDATA_ROOT=...`** (sección 4) sí es correcto per-cuenta — cada
   usuario necesita el suyo propio, apuntando a su propio `$HOME`.

Regla práctica: antes de la primera campaña real en una cuenta nueva, correr
el `--dry-run` de la sección 8.4 y confirmar `pre-flight OK` — si alguna
ruta de `models.yaml`/`campaign.yaml` no existe en la cuenta nueva, aparece
ahí, clase por clase, antes de gastar cupo de cómputo.


## 3. Crear el entorno Python (venv)

**No uses el módulo Python por defecto de NLHPC para crear el venv.** El
módulo por defecto (`python/3.11.x-zen4-*`, vía Spack) está compilado con
instrucciones AVX512 específicas del CPU del login node (AMD EPYC, Zen4).
Los nodos de cómputo de las particiones `general`/`largemem` son Intel
Xeon Gold 6152 (Skylake-SP) — no las soportan, y el intérprete de Python
del venv crashea con `Illegal instruction (core dumped)` al arrancar
*dentro de un job SLURM*, no en el login node donde lo creaste (por eso
pasa desapercibido hasta que ya lanzaste algo). Detalle completo del
diagnóstico: `README.md`, "Decisiones y correcciones", ítem 13.

Usa el módulo `-legacy-skylake` que NLHPC provee justo para este caso:

```bash
module avail python                        # confirma el nombre exacto disponible
module load python/3.12.3-legacy-skylake    # NO el default (zen4)
python3 -m venv pipeline/venv
source pipeline/venv/bin/activate
```

Tu prompt debería mostrar `(venv)` al inicio — esa es la señal de que el
venv está activo.

**Instala las dependencias:**

```bash
pip install --upgrade pip
pip install -r pipeline/requirements.txt
pip install healpy astropy fitsio rubin-sim
git clone https://github.com/LSSTDESC/OpSimSummaryV2.git ~/OpSimSummaryV2
pip install ~/OpSimSummaryV2
```

Notas:
- `healpy` instala como wheel precompilado en Linux (NLHPC) — en Windows no
  compila, así que la Capa 1 contra un `.db` real solo corre en NLHPC.
- `opsimsummaryv2` no está en PyPI — por eso se clona e instala desde GitHub.
- **No instales `pyarrow`.** No hace falta: el pipeline no genera Parquet
  (los `.FITS` que produce SNANA ya son el dataset final — ver README).

Esto puede tardar varios minutos (numpy/pandas/astropy compilan bastante) —
es normal, es una instalación única.


## 4. Cargar SNANA y las variables de entorno

NLHPC ya tiene SNANA instalado como módulo (Lmod) — no lo compilas tú:

```bash
module load SNANA/11.05p
export SNDATA_ROOT=/home/<tu_usuario>/SNDATA_ROOT
```

**Ojo con mayúsculas:** es `SNANA/11.05p`, no `snana/11.05p` — Lmod
distingue mayúsculas de minúsculas y falla en silencio con el nombre mal
escrito (dice "módulo no encontrado", no te avisa que fue un problema de
capitalización).

Si `$SNDATA_ROOT` todavía no existe como carpeta, créala:

```bash
mkdir -p "$SNDATA_ROOT"
```


## 5. Verificación completa del entorno

Antes de seguir, confirma que las 3 piezas (venv, módulo SNANA, variables)
están realmente activas:

```bash
which snlc_sim.exe        # debe imprimir una ruta, no "not found"
echo $SNDATA_ROOT          # debe imprimir tu ruta, no vacío
python -c "import healpy, opsimsummaryv2, rubin_sim, pandas, astropy; print('OK')"
```

Si las tres líneas funcionan sin error, tu entorno está listo. Si algo
falla, vuelve a la sección correspondiente (3 o 4) antes de continuar —
no tiene sentido seguir con un entorno a medias.

**A partir de ahora, cada vez que abras una sesión nueva** (te desconectaste
y volviste a entrar por SSH), no repitas los pasos 3-4 a mano — usa:

```bash
cd ~/AUTOSIM
source activate_all.sh
```

Este script busca el venv solo, carga el módulo, exporta `$SNDATA_ROOT`, y
termina con la misma verificación de arriba. Siempre con `source` (nunca
ejecutándolo directo con `./activate_all.sh` o `bash activate_all.sh`) —
si no, las variables que exporta no quedan activas en tu sesión.


## 6. La guarda anti-login-node — qué es y cómo se ve

Dos pasos del pipeline son cómputo pesado y **se niegan a correr fuera de un
job SLURM**: `build_simlib` (Capa 1, contra un `.db` real) y `postprocess
--campaign` (Capa 4, sobre muchas clases). Si los corres directo en el login
node vas a ver esto y el comando se detiene sin hacer nada:

```
  ✗ ✗ ✗  BLOQUEADO: este paso NO se puede correr en el login node.  ✗ ✗ ✗

  «build_simlib (Capa 1)» es computo pesado. NLHPC ya advirtio por esto una vez —
  correrlo interactivo en el login afecta a todos los usuarios del cluster.

  Correcto (via SLURM):
      sbatch slurm/build_simlib.sbatch baseline_v5.3.1_10yrs WFD
  ...
```

Esto es intencional y es bueno que aparezca — significa que el guardia te
salvó de repetir el problema. La solución siempre es la misma: copiar el
comando `sbatch ...` que el propio mensaje te muestra, en vez de correr el
comando `python -m pipeline....` directo. La sección 8 usa `sbatch` para
justo estos dos pasos.

Si en algún momento *sabes* que el caso es chico y el propio README lo
documenta como aceptable en login (por ejemplo `postprocess` sobre la
campaña de prueba de 2 clases), puedes forzarlo con `--allow-login` — pero
es la excepción, no la forma normal de trabajar.


## 7. Conceptos mínimos de SLURM que vas a usar

Solo necesitas 3 comandos para todo este proyecto:

| Comando | Para qué |
|---|---|
| `sbatch archivo.sbatch [args...]` | encola un trabajo; imprime `Submitted batch job <ID>` |
| `squeue -u $USER` | muestra tus trabajos en cola/corriendo; cuando un trabajo desaparece de esta lista, terminó (bien o mal) |
| `ls logs/*.out logs/*.err` (o donde el script diga) | revisa el resultado — `.out` es la salida normal, `.err` los errores |

Un trabajo "terminado" no es lo mismo que un trabajo "exitoso" — siempre
revisa el `.out`/`.err` después de que `squeue` deje de mostrarlo. La
sección 8 te dice exactamente qué buscar en cada paso.


## 8. Primera corrida guiada: `test_small` de punta a punta

`test_small` es una campaña mínima (2 clases, `NGEN` chico) pensada para
validar que todo el pipeline funciona antes de lanzar la campaña real (42
clases). Sigue los pasos en orden — cada uno depende del anterior.

### 8.1 — Registrar y descargar la base OpSim (Capa 0, login node)

```bash
python -m pipeline.fetch_opsim --list
python -m pipeline.fetch_opsim --run baseline_v5.3.1_10yrs
```

Esto descarga un archivo `.db` (puede pesar cientos de MB — es solo
descarga de red, por eso corre en login sin problema). Espera a que termine
antes de seguir; verás una barra de progreso.

### 8.2 — Generar el SIMLIB (Capa 1, vía SLURM — obligatorio)

```bash
mkdir -p logs
sbatch slurm/build_simlib.sbatch baseline_v5.3.1_10yrs WFD
squeue -u $USER
```

Espera a que el job desaparezca de `squeue` (puede tardar minutos), y
confirma que terminó bien:

```bash
grep -i "error\|traceback" logs/build_simlib_*.out logs/build_simlib_*.err
ls -la data/simlib/baseline_v5.3.1_10yrs/
```

Si `grep` no encuentra nada y el `.SIMLIB` existe y pesa más de un par de MB
(no unos pocos KB), vas bien. Si algo falla, lee el `.err` completo — casi
siempre dice exactamente qué faltó (módulo no cargado, `.db` no descargado, etc.).

### 8.3 — Compilar la campaña (Capa 2, login node — es liviano)

```bash
python -m pipeline.compile_campaign --config campaigns/test_small.yaml
```

Esto solo escribe archivos de texto (milisegundos) — no necesita `sbatch`.
Revisa que se creó `build/test_small/campaign_manifest.json`.

### 8.4 — Validar y lanzar la simulación (Capa 3)

```bash
# primero solo valida, no lanza nada todavia:
python -m pipeline.run_campaign --launch campaigns/test_small.yaml --dry-run
```

Si el resumen dice `pre-flight OK`, lanza de verdad:

```bash
python -m pipeline.run_campaign --launch campaigns/test_small.yaml
```

Esto hace `sbatch` por cada clase de la campaña (2, en `test_small`) — el
cómputo real (`snlc_sim.exe`) corre en esos jobs, no en tu terminal.

**Espera a que terminen** antes de seguir:

```bash
squeue -u $USER                                          # hasta que no aparezcan
python -m pipeline.run_campaign --status build/test_small  # resumen
grep -i "DONE EVERYTHING\|ABORT\|FATAL" build/test_small/*.out
```

Sigue solo cuando veas `DONE EVERYTHING` para cada clase.

### 8.5 — Post-proceso: QC sobre los FITS (Capa 4)

`test_small` tiene solo 2 clases — el propio README lo documenta como
aceptable en login, así que hace falta el override explícito:

```bash
python -m pipeline.postprocess --campaign build/test_small --allow-login
```

Vas a ver una advertencia (es normal, la pediste tú con `--allow-login`) y
después el progreso por clase. Revisa que se generaron los gráficos:

```bash
ls build/test_small/postproc/*/qc/*.png
```

Para la campaña completa (42 clases) **no** uses `--allow-login` — usa
`sbatch` (ver sección 9).

### 8.6 — Etiquetar procedencia (Capa 5, login node)

```bash
python -m pipeline.tag_campaign --campaign build/test_small
```

Genera un `.provenance.json` por clase y un manifiesto consolidado — solo
hashea archivos que ya existen, es instantáneo.

Si llegaste hasta acá sin errores, el pipeline completo funciona en tu
cuenta de NLHPC.


## 9. Escalar a la campaña completa

Repite los pasos 8.3–8.6 con `campaigns/full_v5.3.yaml` en vez de
`test_small.yaml` (42 clases × WFD+DDF = 84 corridas). La única diferencia
real es la Capa 4: con tantas clases, el post-proceso **no** es un caso
aceptable en login — usa `sbatch`:

```bash
sbatch slurm/run_pipeline_step.sbatch pipeline.postprocess --campaign build/full_v5.3
```

Todo lo demás (compilar, lanzar, monitorear, tag) es igual que en la sección 8.


## 10. Problemas comunes

**`ModuleNotFoundError` al importar algo (`healpy`, `opsimsummaryv2`, etc.)**
El venv no está activo, o instalaste en el venv equivocado. Verifica con
`which python` — debe apuntar dentro de `pipeline/venv/`. Si no, corre
`source activate_all.sh` de nuevo.

**`module: command not found` o `Lmod has detected the following error`**
Estás probablemente en un nodo o entorno sin Lmod, o el nombre del módulo
está mal escrito. Confirma mayúsculas exactas: `SNANA/11.05p`.

**El SIMLIB de la sección 8.2 pesa muy poco (unos KB)**
Es casi seguro un SIMLIB de prueba (corrida con `--limit` alguna vez, o el
job falló antes de escribir el archivo completo). Vuelve a correr el
`sbatch` de la sección 8.2 y revisa el `.err` completo esta vez.

**Veo el mensaje `BLOQUEADO: este paso NO se puede correr en el login node`**
Es la guarda funcionando como debe (sección 6) — no es un bug. Copia el
comando `sbatch ...` que el mismo mensaje te muestra.

**`sbatch: command not found`**
No estás en un nodo con acceso a SLURM, o tu sesión SSH cayó en algo
distinto al login node de NLHPC. Revisa cómo te conectaste.

**Un job aparece y desaparece de `squeue` casi al instante**
Probablemente falló apenas arrancó (típico: `.err` con
`venv/bin/activate: No such file or directory`, o módulo mal escrito). Lee
siempre el `.err` — un job que "ya no está en cola" no significa que haya
terminado bien.

**Nada de esto corre en mi computador (Windows/Mac) fuera de NLHPC**
Es esperado para la Capa 1 contra un `.db` real (`healpy` no compila fácil
fuera de Linux) y para cualquier paso que necesite `snlc_sim.exe` (el
binario de SNANA solo existe como módulo en NLHPC). Los `--self-test` de
`build_simlib.py` y `postprocess.py` sí corren en cualquier máquina con las
dependencias de Python instaladas — son sintéticos, sin `.db` ni FITS
reales, y sirven para validar que el código en sí funciona.


## 11. Siguientes pasos

Con `test_small` corriendo de punta a punta, ve a [`README.md`](README.md)
para:
- Entender la arquitectura completa por capas
- Agregar una clase de transiente nueva (`models.yaml`)
- Agregar una versión nueva de OpSim (`opsims.yaml`)
- Revisar las decisiones técnicas ya tomadas y por qué (evita repetir
  debugging ya resuelto)
