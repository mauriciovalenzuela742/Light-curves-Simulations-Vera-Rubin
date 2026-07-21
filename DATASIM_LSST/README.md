# DATASIM_LSST - Input Files para Simulaciones SNANA

## Descripción

Esta carpeta contiene los archivos de configuración `.INPUT` y scripts SLURM para ejecutar simulaciones de curvas de luz usando SNANA en el cluster NLHPC, para el proyecto Vera Rubin Legacy Survey of Space and Time (LSST).

## Estructura de directorios

```
DATASIM_LSST/
├── WFD/
│   └── input_files_v6/
│       ├── AGN/
│       ├── EB/
│       ├── ... (38 clases)
│       └── uLens-Single-PyLIMA/
|   └── input_files_v7/
│       ├── AGN/
│       ├── EB/
│       ├── ... (38 clases)
│       └── uLens-Single-PyLIMA/
│
└── DDF/
    └── input_files_v6/
       ├── AGN/
       ├── EB/
       ├── ... (38 clases)
       └── uLens-Single-PyLIMA/
    └── input_files_v7/
        ├── AGN/
        ├── EB/
        ├── ... (38 clases)
        └── uLens-Single-PyLIMA/
```

## Versiones

### input_files_v6
- **Fecha de generación**: 2025-10-20
- **Fecha configurada**: 20251020
- **SIMLIB versión**: 5.0
- **Estado**: Estable, lista para producción

### input_files_v7
- **Fecha de generación**: 2026-07-20
- **Fecha configurada**: 20260720
- **SIMLIB versión**: 5.3
- **Estado**: Estable, lista para producción

## Planes de Observación (solo cambia el numero de la version en los directorios)

### WFD (Wide Field Deep)
- Simulaciones para el programa de campo ancho profundo
- 38 clases de objetos
- SIMLIB: `/home/mvalenzuela/SIMLIBv5.3/WFD_SIMLIBv5.3.SIMLIB`

### DDF (Deep Drilling Fields)
- Simulaciones para los campos de perforación profunda
- 38 clases de objetos
- SIMLIB: `/home/mvalenzuela/SIMLIBv5.3/DDF_SIMLIBv5.3.SIMLIB`

## Clases disponibles

AGN, CaRT, Cepheid, Dwarf_nova, EB, ILOT, KN-BULLA-BNS-M2-2COMP, KN-BULLA19, KN-K17, M-dwarf, Mdwarf-flare, Mira, PISN, PISN-STELLA-HECORE, PISN-STELLA-HYDROGENIC, RRL, SLSN-I, SLSN-I_NON1ASED, SNII-NMF, SNII-templates, SNIIn-MOSFIT, SNIa, SNIa-91bg, SNIa-91bg_NON1ASED, SNIax, SNIb-templates, SNIc-templates, TDE, V19_SNII, V19_SNIIb, V19_SNIIn, V19_SNIb, V19_SNIc, V19_SNIcBL, VC25_SNII, VC25_SNIbc, d-Scuti, uLens-Binary, uLens-Single-GenLens, uLens-Single-PyLIMA

## Uso

### Ejecutar una simulación
```bash
cd WFD/input_filesv7/AGN
sbatch run_AGN_WFD_20260720.sh
```

### Monitorear
```bash
squeue -u $USER
tail -f run_AGN_*.err.out
```

## Historial

| Versión | Fecha | Cambios |
|---------|-------|---------|
| v6 | 2025-10-20 | SIMLIBv5.3, fecha 20251020 |
| v7 | 2026-07-20 | SIMLIBv5.3, fecha 20260720 |

## Contacto

Email: maosvalenzuela@gmail.com
