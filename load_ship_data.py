import xarray as xr
import time
import ast  # for readign configuration file
import algae_tools as agt
import os
import re
import datetime as dt
import numpy as np

conf_dat = agt.conf_dat 
agt.read_cmd_params()
target_date = agt.model_parameters['forecast_time']
if(target_date == ''):
    target_date = dt.datetime.now()
oper_dir = conf_dat['oper_dir']
rawdata_name = "ship_data.csv"
savefile_name = "ship_data.nc"
scp_command_base ="scp {}@{}:{}/{} {}"  

file_filter = '*.mit'
ship_server = 'lighthouse.fmi.fi'
remote_path = '/data1/silja_serenade/instruments/Algaline/current/'
remote_files = os.popen('ssh {}@{} "ls -rt {}{}"'.format(\
        conf_dat['shipdata_login'],\
        ship_server,\
        remote_path,
        file_filter)).read()

remote_files = remote_files.strip().split('\n')
min_diff = None
remote_file = ""
for rf in remote_files: # search for the closest match:
    date = re.search('_(.{8})[^_]*\.mit',rf).groups()[0]
    date = dt.datetime.strptime(date,'%Y%m%d')
    if(not min_diff or np.abs(date - target_date) < min_diff):
        min_diff = np.abs(date - target_date)
        remote_file = rf
remote_file = re.search('[^/]*$',remote_file).group() #actual filename


scp_command = scp_command_base.format(\
        conf_dat['shipdata_login'],\
        ship_server,\
        remote_path,\
        remote_file,\
        oper_dir

        )
result = os.system(scp_command)
print("Aquired {1} from {0}".format(ship_server, remote_file))
py_command = "python point_to_grid.py --infile {} --outfile {}".format(\
        remote_file, savefile_name)
print(py_command)
os.system(py_command)
