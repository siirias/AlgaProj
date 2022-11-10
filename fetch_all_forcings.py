"""
Simple script to just run all the parts of the suite
which gather data from various sources
"""
import os

os.system('python load_hydrodyn_forcing.py')
os.system('python load_athmospheric_forcing.py')
os.system('python load_wave_forcing.py')
os.system('python load_bgc_forcing.py')
os.system('python load_satellite_forcing.py')
os.system('python load_ship_data.py')

os.system('python set_grid_sizes.py')

