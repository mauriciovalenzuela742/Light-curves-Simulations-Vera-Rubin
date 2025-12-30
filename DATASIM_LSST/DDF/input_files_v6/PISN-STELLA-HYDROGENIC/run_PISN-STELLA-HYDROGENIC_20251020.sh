#!/bin/bash
#---------------Script SBATCH - NLHPC ----------------
#SBATCH -J run_PISN-STELLA-HYDROGENIC
#SBATCH -p general
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem-per-cpu=1000
#SBATCH --mail-user=maosvalenzuela@gmail.com
#SBATCH --mail-type=ALL
#SBATCH -o run_PISN-STELLA-HYDROGENIC_%A_%a.err.out
#SBATCH -e run_PISN-STELLA-HYDROGENIC_%A_%a.err.out

#-----------------Toolchain---------------------------
# ----------------Modulos----------------------------
ml  SNANA/11.05p  
# ----------------Comando--------------------------
export SNDATA_ROOT=/home/mvalenzuela/SNDATA_ROOT

snlc_sim.exe PISN-STELLA-HYDROGENIC_20251020.input
