#!/bin/bash
#-------------- Script SBATCH - NLHPC ----------------
#SBATCH -J plots_SNANA
#SBATCH -p general
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem-per-cpu=1000
#SBATCH --mail-user=maosvalenzuela@gmail.com
#SBATCH --mail-type=ALL
#SBATCH -o plots_SNANA_%j.out
#SBATCH -e plots_SNANA_%j.err

#-------------- Entorno ----------------
ml python
source ~/venvs/snana/bin/activate

#-------------- Comando ----------------
TOOLS_DIR=/home/mvalenzuela/run_SNANA/tools
DATE=20241202   # <<< ajusta la fecha de la tanda que quieres procesar

bash $TOOLS_DIR/run_all_plots.sh $DATE

echo "Listo. Revisa ${PLOTS_BASE}"
