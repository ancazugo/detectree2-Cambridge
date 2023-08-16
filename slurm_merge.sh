#!/bin/bash
#SBATCH --partition high-mem
#SBATCH --mem 256000
#SBATCH --ntasks 16
#SBATCH --time 48:00:00
#SBATCH --output %j.out
#SBATCH --error %j.err

# python merge_tiffs.py0
conda activate detectree2-env
python stitch_crowns.py