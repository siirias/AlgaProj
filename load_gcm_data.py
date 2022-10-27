import fmiopendata
from fmiopendata.wfs import download_stored_query as fmi_dsq
import xarray as xr


oper_dir = "/mnt/c/Data/alga_test/"
product_name = "fmi::forecast::harmonie::surface::grid"
product_args = ["bbox=16,59,30,66"]
#product_args = ["bbox=18,59,20,60"]
variables = ['Mean sea level pressure', 'Surface net solar radiation']
grid_type = 'latlon'    # latlon means we can store just first lat-lon rows.
                        # Anything else means the whole grid must be saved
print('fetching metadata...')
model_data = fmi_dsq(product_name, args = product_args)
last_data = model_data.data[max(model_data.data.keys())]
print('fetching data...')
last_data.parse(delete = True)

gathered_data = {}
latitudes = last_data.latitudes
longitudes = last_data.longitudes
time_axis = list(last_data.data.keys())
layers = last_data.data[min(time_axis)].keys()
if( grid_type == 'latlon'):
    gathered_data['lat'] = (('lat',), latitudes[:,0])
    gathered_data['lon'] = (('lon',), longitudes[0,:])
else:
    gathered_data['latitude'] = (('lat','lon'), latitudes)
    gathered_data['longitude'] = (('lat','lon'), longitudes)
gathered_data['time'] = (('time',), time_axis)

for var in variables:
    the_unit = last_data.data[min(time_axis)][min(layers)][var]['units']
    print("{} ({}), size = {}".format(var, \
            the_unit, \
            last_data.data[min(time_axis)][min(layers)][var]['data'].shape))
    new_var = []
    for time in time_axis:
        data = last_data.data[time]
        data = data[min(data.keys())] # take the lowest layer
        new_var.append(xr.DataArray(data[var]['data'], dims = ['lat','lon'], attrs = {'units':the_unit}))
#    gathered_data[var] = (('time','lat','lon'),xr.concat(new_var, dim = time_axis))
    gathered_data[var] = xr.concat(new_var, dim = xr.DataArray(time_axis, dims = 'time'))


data_xr = xr.Dataset(gathered_data)
data_xr.to_netcdf(oper_dir + "meteor_data.nc")
