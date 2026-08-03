# run_SNANA — recursos compartidos del survey (no específicos de una clase)

## Descripción

A diferencia de `model_config/` (un archivo por clase), esta carpeta contiene
los recursos que **todas** las simulaciones comparten, sin importar la clase:

| Archivo | Qué es |
|---|---|
| `kcor_LSST.fits` | Tabla de corrección-K + curvas de transmisión de los 6 filtros LSST (`ugrizY`) — clave `KCOR_FILE` |
| `LSST_photoz_G18.HOSTLIB` | Catálogo de galaxias anfitrionas con foto-z (Graham+2018) — clave `HOSTLIB_FILE` |
| `LSST_SEARCHEFF_PIPELINE.DAT` | Curva de eficiencia de detección del pipeline de búsqueda — clave `SEARCHEFF_PIPELINE_FILE` |
| `LSST_PIPELINE_LOGIC.DAT` | Lógica de qué combinación de detecciones cuenta como "hallazgo" — clave `SEARCHEFF_PIPELINE_LOGIC_FILE` |

## Dónde se usa

El pipeline **[ALCeS](https://github.com/mauriciovalenzuela742/ALCeS)**
referencia estos archivos una sola vez, a nivel de todo el survey, en el
`include_survey_{WFD,DDF}_<run>.INPUT` que genera automáticamente
`pipeline/campaign/templates.py` — no varían por clase.
