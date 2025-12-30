#!/bin/bash
#---------------Script SBATCH - NLHPC ----------------
#SBATCH -J run_KN-BULLA19
#SBATCH -p general
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem-per-cpu=1000
#SBATCH --mail-user=maosvalenzuela@gmail.com
#SBATCH --mail-type=ALL
#SBATCH -o run_KN-BULLA19_%A_%a.err.out
#SBATCH -e run_KN-BULLA19_%A_%a.err.out

#-----------------Toolchain---------------------------
# ----------------Modulos----------------------------
ml  SNANA/11.05p  
# ----------------Comando--------------------------
export SNDATA_ROOT=/home/mvalenzuela/SNDATA_ROOT

snlc_sim.exe KN-BULLA19_20251020.input
