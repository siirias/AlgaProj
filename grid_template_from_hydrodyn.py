"""
A rather hacky script to create the grid_template.nc
To do, you should first download data with the 
load_hydrodyn_forcing.py, then use that as basis.
This way the template matches the hydrodyn.
"""
import ast
import numpy as np
import xarray as xr
conf_dat = ast.literal_eval("".join(open('config.txt').readlines()))
oper_dir = conf_dat['oper_dir']

dat = xr.open_dataset(oper_dir+'hydrodyn_data.nc')
x = dat['Ocean potential temperature'].data
x = x[0,:,:]
land_mask = np.vectorize(lambda a: not np.isnan(a))(x)
tmp = xr.DataArray(land_mask, dims = ['lat','lon'])
new_set = xr.Dataset({'land_mask':tmp, 'lat':dat['lat'], 'lon':dat['lon']})
new_set.to_netcdf(oper_dir+'grid_template.nc')

