import xarray as xr
import time
import algae_tools as agt
import os
import re
import datetime as dt
import xarray as xr
import numpy as np
import pandas as pd

conf_dat = agt.conf_dat 
oper_dir = conf_dat['oper_dir']
config_dir = conf_dat['config_dir']
agt.read_cmd_params()
max_iterations = 20

cfl_ind = 'Sopcfl'
if 'in_file' in agt.model_parameters.keys():
    in_file_name = agt.model_parameters['in_file']
else:
    in_file_name = 'SS_20221108150730.mit'
if 'out_file' in agt.model_parameters.keys():
    savefile_name = agt.model_parameters['out_file']
else:
    savefile_name = 'ship_data.nc'

#Read the in fiel as pandas object:
csv_dat = pd.read_csv(oper_dir + in_file_name, sep='\t', parse_dates = ['Date'])

# Shape the needed grid format.
the_grid = xr.open_dataset(config_dir + agt.model_parameters['grid_template'])
gridded_data = np.zeros(the_grid.land_mask.shape)
lat = np.array(the_grid.lat)
lon = np.array(the_grid.lon)

algae_grid = xr.DataArray(gridded_data.copy(), \
        dims = ['lat', 'lon'], \
        attrs = {'units':'g/m3'},\
        coords={'lat':lat, 'lon':lon})
samples_grid = xr.DataArray(gridded_data.copy(),\
        dims = ['lat', 'lon'], \
        attrs = {'units':'samples'},\
        coords={'lat':lat, 'lon':lon})
for i,lat_i, lon_i in zip(csv_dat[cfl_ind],csv_dat['Lat'],csv_dat['Lon']):
    if(     lat_i >= np.min(lat) and lat_i <= np.max(lat) and\
            lon_i >= np.min(lon) and lon_i <= np.max(lon)):
        lat_index = np.argmin(np.abs(lat - lat_i))
        lon_index = np.argmin(np.abs(lon - lon_i))
        algae_grid[lat_index, lon_index] += i
        samples_grid[lat_index, lon_index] += 1

algae_grid = algae_grid.where(samples_grid>0) #get rid of divide by zeros
algae_grid = algae_grid/samples_grid

#expand values around np.nan's to get more coverage
[algae_grid_interpolated, interpolation_distances] = \
        agt.fill_empty_data(algae_grid, the_grid, max_iterations, 'g/m^3')

database = {'lat':the_grid.lat, 'lon':the_grid.lon, \
        'algae':algae_grid, 'algae_interp':algae_grid_interpolated,\
        'interp_distances':interpolation_distances, 'samples':samples_grid}
data_xr = xr.Dataset(database)
data_xr = agt.add_meta_data(data_xr)
data_xr.to_netcdf(oper_dir + savefile_name, 'w')
print("Saved: {}".format(oper_dir + savefile_name))
