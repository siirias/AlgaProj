import xarray as xr
import numpy as np
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
start_condition_filename = 'start_condition.nc'
distance_weight = 5 # samller means distance weight drops faster

def algae_from_default(data):
    return data
def algae_from_ship(data):
    d = data * 3.0
    d_min = np.vectorize(lambda x: min([x,1.0]))
    d = d_min(d)
    return d

def weight_from_distance(distances):
    def d_to_weight(dist):
        if(dist <1.0):
            dist = 1.0 #avoid div by 0
        weight = distance_weight/(dist+distance_weight -1)
        if weight < 0.02:
            weight = 0.0
        return weight
    d_to_weight = np.vectorize(d_to_weight)
    return d_to_weight(distances)

expand_iterations = 20
# First, fill empty areas on input grids to some degree.
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

files_to_handle = ['satellite_data_regridded_e.nc','ship_data_e.nc']
handlers = [algae_from_default, algae_from_ship]

end_result = agt.default_area.grid
total_value = np.zeros(end_result.land_mask.shape)
total_weight = np.zeros(end_result.land_mask.shape)
reliability = np.zeros(end_result.land_mask.shape)
for f,h in zip(files_to_handle, handlers):
    dat = xr.open_dataset(oper_dir + f).load()
    values = np.array(h(dat['algae_expanded']))
    distances = np.array(dat['algae_exp_distance'])
    weight = weight_from_distance(distances)
    total_value[np.invert(np.isnan(values))] += (weight * values)[np.invert(np.isnan(values))]
    total_weight[np.invert(np.isnan(weight))] += weight[np.invert(np.isnan(weight))]
    reliability[reliability<weight] = weight[reliability<weight]
total_value = total_value / total_weight


end_result = end_result.assign({'algae':xr.DataArray(total_value, dims = ['lat','lon']),\
    'reliability':xr.DataArray(reliability, dims = ['lat', 'lon'])})
end_result.to_netcdf(oper_dir + start_condition_filename,'w')


