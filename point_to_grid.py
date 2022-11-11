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
max_iterations = 40

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

#let's still try to interpolate
# This part later to it's own piece
# this piece uses lots of flattened arrays, as many
# logical operations won't work on 2d arrays.
ag_orig = np.array(algae_grid.copy())
ag_tmp = algae_grid.copy()
true_shape = ag_tmp.shape
ag_orig_l = np.reshape(ag_orig,(true_shape[0]*true_shape[1]))
land_mask_l = np.reshape(np.array(the_grid.land_mask),(true_shape[0]*true_shape[1]))
ag_calculated = ag_orig_l.copy() # which values are alraedy calculated
ag_distances = np.ones((true_shape[0]*true_shape[1]))
ag_distances[:] = np.nan  #where there is no data
ag_distances[np.invert(np.isnan(ag_orig_l))] = 0 #actual data
ext_step = 0
for i in range(max_iterations):
    ag_base = np.array(ag_tmp)
    ag_u = np.roll(ag_base,-1,0)
    ag_d = np.roll(ag_base,1,0)
    ag_l = np.roll(ag_base,-1,1)
    ag_r = np.roll(ag_base,1,1)
    ag_ul = np.roll(ag_l,-1,0)
    ag_dl = np.roll(ag_l,1,0)
    ag_dr = np.roll(ag_d,1,1)
    ag_ur = np.roll(ag_u,1,1)
    ag_tmp = np.nanmean(np.stack((ag_u, ag_d, ag_l, ag_r,\
                                ag_ul, ag_dl, ag_dr, ag_ur)),0)

    ag_tmp = np.reshape(ag_tmp,(true_shape[0]*true_shape[1]))
    orig_filter = np.invert(np.isnan(ag_orig_l))
    ag_tmp[orig_filter] = ag_orig_l[orig_filter] # make sure to keep original
    ag_tmp[land_mask_l < 0.5] = np.nan  # remove points from land, to prevent propagation
    ag_distances[np.logical_xor(np.isnan(ag_tmp), np.isnan(ag_calculated))] = i+1
    ag_calculated = ag_tmp.copy()  #protects the already calculated values.
    ag_tmp = np.reshape(ag_tmp, true_shape)    


ag_distances = np.reshape(ag_distances, true_shape)    
algae_grid_interpolated = xr.DataArray(ag_tmp, \
        dims = ['lat', 'lon'], \
        attrs = {'units':'g/m3'},\
        coords={'lat':lat, 'lon':lon})
interpolation_distances = xr.DataArray(ag_distances, \
        dims = ['lat', 'lon'], \
        attrs = {'units':'cell'},\
        coords={'lat':lat, 'lon':lon})


# end of interpolation
database = {'lat':the_grid.lat, 'lon':the_grid.lon, \
        'algae':algae_grid, 'algae_interp':algae_grid_interpolated,\
        'interp_distances':interpolation_distances, 'samples':samples_grid}
data_xr = xr.Dataset(database)
data_xr = agt.add_meta_data(data_xr)
data_xr.to_netcdf(oper_dir + savefile_name, 'w')
print("Saved: {}".format(oper_dir + savefile_name))
