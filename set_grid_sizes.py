import xarray as xr
import time
import ast  # for readign configuration file
import algae_tools as agt
import os
import sys
import datetime as dt
import re

conf_dat = agt.conf_dat
agt.read_cmd_params()
oper_dir = conf_dat['oper_dir']
config_dir = conf_dat['config_dir']
agt.read_cmd_params()

for file_name in agt.model_parameters['files2newgrid']:
    new_file_name =  re.sub('\.nc','_regridded.nc',file_name)
    cdo_command = "cdo remapbil,{} {} {}".\
            format(config_dir + agt.model_parameters['grid_template'],\
                   oper_dir + file_name,\
                   oper_dir + new_file_name)
    os.system(cdo_command)
    if(agt.model_parameters['del_temp_files'] and os.path.isfile(oper_dir + new_file_name)):
            print('should delete {}'.format(file_name))
            os.remove(oper_dir + file_name)

