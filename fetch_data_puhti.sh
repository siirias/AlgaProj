#!/bin/bash
module purge
module load tykky
export PATH="/projappl/project_2001981/siiriasi/AGEnv/bin/:$PATH"
cd /projappl/project_2001981/siiriasi/algae_proj/
python fecth_all_forcings.py

