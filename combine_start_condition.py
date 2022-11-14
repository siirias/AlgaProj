import xarray as xr
import ast  # for readign configuration file
import algae_tools as agt
import os
import sys
import re
conf_dat = agt.conf_dat
oper_dir = conf_dat['oper_dir']
config_dir = conf_dat['config_dir']
agt.read_cmd_params()
expandable_variables = ['algae']

expand_iterations = 20

file_list = agt.model_parameters['files2expand']
for f in file_list:
    dat = xr.open_dataset(oper_dir + f).load()
    for v in dat.keys():
        var_name = v + '_expanded'
        dist_name = v + '_exp_distance'
        if(v in expandable_variables and var_name not in dat.keys()):
            if('units' in dat[v].attrs):
                unit = dat[v].attrs['units']
            else:
                unit = '-'
            [var_expanded, var_distances] = agt.fill_empty_data(\
                    dat[v], None, expand_iterations, unit)
            dat = dat.assign({var_name:var_expanded, dist_name:var_distances})
    new_f = re.search('(.*)\.nc',f).groups()[0]+'_e.nc'
    dat.to_netcdf(oper_dir + new_f,'w')

