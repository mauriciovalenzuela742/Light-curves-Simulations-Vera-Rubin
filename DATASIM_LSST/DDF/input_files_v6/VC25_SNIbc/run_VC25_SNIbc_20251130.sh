#!/bin/bash
#---------------Script SBATCH - NLHPC ----------------
#SBATCH -J run_VC25_SNIbc
#SBATCH -p general
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem-per-cpu=1000
#SBATCH --mail-user=maosvalenzuela@gmail.com
#SBATCH --mail-type=ALL
#SBATCH -o run_VC25_SNIbc_%A_%a.out
#SBATCH -e run_VC25_SNIbc_%A_%a.err

#-----------------Toolchain---------------------------
# ----------------Modulos----------------------------
ml  SNANA/11.05p  
# ----------------Comando--------------------------
export SNDATA_ROOT=/home/mvalenzuela/SNDATA_ROOT

snlc_sim.exe VC25_SNIbc_20251130.input
