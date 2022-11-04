import fmiopendata
from fmiopendata.wfs import download_stored_query as fmi_dsq
import xarray as xr
import time
import ast  # for readign configuration file
import algae_tools as agt
import os
import re
import datetime as dt

conf_dat = ast.literal_eval("".join(open('config.txt').readlines()))
oper_dir = conf_dat['oper_dir']
rawdata_name = "ship_data.csv"
savefile_name = "ship_data.nc"
scp_command_base ="scp {}@{}:{}/{} {}"  

file_filter = '*.mit'
ship_server = 'lighthouse.fmi.fi'
remote_path = '/data1/silja_serenade/instruments/Algaline/current/'
remote_file = os.popen('ssh {}@{} "ls -lrth {}{}"'.format(\
        conf_dat['shipdata_login'],\
        ship_server,\
        remote_path,
        file_filter)).read()
remote_file = remote_file.strip().split('\n')[-1] # last file
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
