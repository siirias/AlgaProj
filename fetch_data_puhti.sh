#!/bin/bash
module purge
module load tykky
export PATH="/projappl/project_2001981/siiriasi/AGEnv/bin/:$PATH"
cd /projappl/project_2001981/siiriasi/algae_proj/
python load_athmospheric_forcing.py
python load_hydrodyn_forcing.py
python load_wave_forcing.py
python load_bgc_forcing.py

