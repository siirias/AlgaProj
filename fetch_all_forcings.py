"""
Simple script to just run all the parts of the suite
which gather data from various sources
"""
import os
import algae_tools as agt
import datetime as dt

conf_dat = agt.conf_dat 
oper_dir = conf_dat['oper_dir']
output_dir = conf_dat['output_dir']
config_dir = conf_dat['config_dir']
agt.read_cmd_params()
t_stamp =  agt.model_parameters['forecast_time']
t_stamp_txt = dt.datetime.strftime(t_stamp, '%Y-%m-%d')
#os.system('python load_hydrodyn_forcing.py -t {}'.format(t_stamp_txt))
#os.system('python load_athmospheric_forcing.py -t {}'.format(t_stamp_txt))
#os.system('python load_wave_forcing.py -t {}'.format(t_stamp_txt))
#os.system('python load_bgc_forcing.py -t {}'.format(t_stamp_txt))
os.system('python load_satellite_forcing.py -t {}'.format(t_stamp_txt))
os.system('python load_ship_data.py -t {}'.format(t_stamp_txt))

os.system('python set_grid_sizes.py -t {}'.format(t_stamp_txt))
os.system('python combine_start_condition.py -t {}'.format(t_stamp_txt))

