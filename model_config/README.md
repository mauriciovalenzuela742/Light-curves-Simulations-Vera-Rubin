# model_config — configuración de modelos SNANA por clase

## Descripción

Esta carpeta contiene los archivos `SIMGEN_INCLUDE_<clase>.INPUT` curados: uno
por cada clase de transiente/variable soportada, con el modelo (`GENMODEL`),
rangos de redshift/fase, pesos de plantillas (`NON1A:` cuando aplica), y
otros parámetros específicos de esa clase ya afinados por prueba y error real
contra SNANA 11.05p.

Estos son los archivos que el pipeline **ALCeS** referencia (uno por línea en
`models.yaml`, vía `simgen_include:`) para generar el `.INPUT` final de cada
simulación — no se reinventan acá, se usan tal cual.

## Convención de nombres

`SIMGEN_INCLUDE_<CLASE>.INPUT` — el nombre después de `SIMGEN_INCLUDE_`
identifica la clase (p.ej. `SIMGEN_INCLUDE_KN-K17.INPUT` → clase `KN-K17`).
Los que empiezan con `LCLIB_` usan el motor de curvas de luz por catálogo
(`GENMODEL: LCLIB`) en vez de un modelo generativo estándar.

## Dónde se usa

Ver el repo **[ALCeS](https://github.com/mauriciovalenzuela742/ALCeS)** —
el pipeline real que consume estos archivos — específicamente
`pipeline/models.yaml`, que mapea cada clase a su ruta real en NLHPC
(`~/run_SNANA/model_config/...`, `~/run_SNANA/elastic/model_config/...`, o
`~/OTMODEL_NON1ASED/SNtypes/...` según la familia).
