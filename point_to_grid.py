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

cfl_ind = 'Sopcfl'
in_file_name = 'SS_20221108150730.mit'
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

#let's still try to interpolate
algae_grid_interpolated = algae_grid.copy()
algae_grid_interpolated.interpolate_na('lat')
algae_grid_interpolated.interpolate_na('lon')

database = {'lat':the_grid.lat, 'lon':the_grid.lon, \
        'algae':algae_grid, 'algae_interp':algae_grid_interpolated,\
        'samples':samples_grid}
data_xr = xr.Dataset(database)
data_xr = agt.add_meta_data(data_xr)
data_xr.to_netcdf(oper_dir + savefile_name, 'w')
print("Saved: {}".format(oper_dir + savefile_name))
