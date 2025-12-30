# Light-curve simulations with SNANA for the Vera Rubin Observatory

This repository provides a **fully reproducible SNANA-based simulation infrastructure** to generate large-scale, multi-class light-curve datasets for the **Vera C. Rubin Observatory (LSST)** under both **Wide-Fast-Deep (WFD)** and **Deep Drilling Field (DDF)** survey strategies.

The pipeline is designed to support **machine-learning applications**, particularly photometric classification, and has been developed and deployed on the **National Laboratory for High Performance Computing (NLHPC, Leftraru)**. The resulting datasets have already been used within the **ALeRCE** collaboration.

---

## 1. Scientific Motivation

Rubin/LSST will detect millions of transient and variable sources every few nights. Because spectroscopic follow-up will be available for only a small fraction of these events, robust **photometric classification** will be essential for scientific exploitation of the survey.

Current training datasets are heavily biased toward Type Ia supernovae and lack sufficient diversity in both core-collapse supernovae and rarer transient classes. This project addresses that limitation by providing a scalable, physically motivated simulation framework capable of generating **balanced and realistic light-curve datasets** tailored to LSST observing conditions.

---

## 2. Survey Strategies: WFD and DDF

Simulations are based on the **baseline_v5.0** family of LSST OpSim/ObSim runs (October 2025), which encode realistic survey execution over 10 years, including cadence, depth, and observing constraints.

* **WFD (Wide-Fast-Deep):** Moderate cadence over a large fraction of the sky.
* **DDF (Deep Drilling Fields):** High-cadence, high-depth observations over a small number of fields, following the v5.0 “Ocean” strategy.

SIMLIB files derived from these OpSim runs are used by SNANA to reproduce the exact survey cadence and depth.

---

## 3. Supported Transient and Variable Classes

The infrastructure supports a wide range of classes, including:

### PLAsTiCC / Standard Templates

* SNIa, SNIa-91bg, SNIax
* SNII (templates, NMF), SNIIn-MOSFIT
* SNIb/c templates
* SLSN-I, TDE
* Kilonovae (KN-K17, KN-BULLA19)
* AGN, RR Lyrae, M-dwarfs, Mira
* Eclipsing binaries, microlensing (single/binary), ILOT, CaRT, PISN

### ELASTiCC Extensions

* d-Scuti
* Dwarf nova, M-dwarf flares
* PISN-STELLA (hydrogenic and He-core)

### NON1ASED (Work in Progress)

* SNIax_NON1ASED
* SNIa-91bg_NON1ASED
* TDE_NON1ASED
* SLSN-I_NON1ASED
* KN-BULLA-BNS-M2COMP_NON1ASED

All classes are simulated under both WFD and DDF strategies when physically appropriate.

---

## 4. Repository Structure

```text
Light-curves-Simulations-Vera-Rubin/
├── run_SNANA/          # SNANA configs, models, and inputs
├── SIMLIB/             # LSST WFD and DDF SIMLIB files
└── DATASIM_LSST/       # Reference LSST simulation inputs and SLURM submission scripts
```

The **DDF and WFD directory trees are structurally identical**, differing only in the SIMLIBs and input files used.

---

## 5. Requirements

* SNANA >= 11.05
* gcc >= 9
* Python >= 3.8
* Access to `SNDATA_ROOT`

### SNDATA_ROOT

The SNANA data repository is required and must be downloaded separately:

[https://zenodo.org/records/12655677](https://zenodo.org/records/12655677)

After downloading, define:

```bash
export SNDATA_ROOT=/path/to/SNDATA_ROOT
```

---

## 6. Running a Simulation

### Example: DDF

```bash
cd DATASIM_LSST
cd DDF
cd input_files_v6
cd AGN
sbatch run_AGN_20251020.sh #this is the version try to simulate
```

### Example: WFD

```bash
cd DATASIM_LSST
cd WFD
cd input_files_v6
cd AGN
sbatch run_AGN_20251020.sh #this is the version try to simulate
```

Batch execution on NLHPC is supported via SLURM scripts in `scripts/`.

---

## 7. Outputs and Machine-Learning Products

SNANA outputs (`PHOT.FITS`, `HEAD.FITS`) are converted into machine-learning–ready tables and organized by class and survey strategy. These datasets have been successfully integrated into the **ALeRCE** pipeline to evaluate computational performance.

---

## 8. Reproducibility

This repository contains all configuration files and models required to reproduce the simulations. Large external datasets (e.g. `SNDATA_ROOT`) are referenced via Zenodo DOIs to ensure long-term availability.

---

## 9. Citation

If you use this work, please cite:

* Kessler et al. (2009), *SNANA: A Public Software Package for Supernova Analysis*, PASP
* Ramírez et al. (2024), arXiv:2409.10701

---

## Author

**Mauricio Valenzuela Corvalán**
Universidad de Chile / ALeRCE / NLHPC
Email: [maosvalenzuela@gmail.com](mailto:maosvalenzuela@gmail.com)

