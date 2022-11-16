import os
import sys
import xarray as xr
import time
import algae_tools as agt
import re
import datetime as dt
import shutil
import ast  # for readign configuration file


conf_dat = agt.conf_dat 
oper_dir = conf_dat['oper_dir']
output_dir = conf_dat['output_dir']
config_dir = conf_dat['config_dir']
agt.read_cmd_params()

if(os.path.isfile(oper_dir + 'last_step.txt')):
    run_status = ast.literal_eval("".join(open(oper_dir + 'last_step.txt').readlines()))
else:
    run_status = {'last_time':dt.datetime.strftime(agt.model_parameters['forecast_time'],'%Y-%m-%d')}

last_time = dt.datetime.strptime(run_status['last_time'], '%Y-%m-%d')
current_time = last_time + dt.timedelta(days = 1 )

# fetch previous condition in oper dir, if available
last_state_fname = 'end_state_{}.nc'.format(dt.datetime.strftime(last_time,'%Y%m%d'))
if(os.path.isfile(output_dir + last_state_fname)):
    shutil.copyfile(output_dir + last_state_fname, oper_dir + 'last_state.nc')

#Will gather all input, and format a start_condition
os.system('python fetch_all_forcings.py -t {}'.format(\
        dt.datetime.strftime(current_time,'%Y-%m-%d')))

#run the actual drifting model
#TBD
#this just copies start condition into end state.
shutil.copyfile(oper_dir + 'start_condition.nc', oper_dir + 'end_state.nc')

#copy end result on storage
files_to_save = ['satellite_data_regridded_e.nc', 'ship_data_e.nc',\
        'start_condition.nc', 'end_state.nc']


for f in files_to_save:
    new_f_pieces = re.search('([^.]*)(\..*)',f).groups()
    new_f = new_f_pieces[0] + \
            dt.datetime.strftime(current_time,'_%Y%m%d')\
            + new_f_pieces[1]
    shutil.copyfile(oper_dir + f, output_dir + new_f)

#step up for next timestep
run_status['last_time'] =  dt.datetime.strftime(current_time,'%Y-%m-%d')
with open(agt.conf_dat['oper_dir'] + 'last_step.txt', 'w') as f:
    f.write(str(run_status))
