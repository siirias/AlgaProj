import fmiopendata
from fmiopendata.wfs import download_stored_query as fmi_dsq
import xarray as xr
import time
"""
The purpose of this script is to provide functions needed in several scripts
that will consist of the alage product.

Currently in:
    format_query(): Returns a dictionary that can be used for fetch_data 
    fetch_data(DataQuery): Fetches data from fmi opendata system, and returns xarray Dataset 
                            that can be saved as netCDF
"""
default_bounding_box = "bbox=16,59,30,66"

def format_query(in_product_name, in_product_args=[], in_parameters=[],*, no_params=False):
    grid_type = 'latlon'  #so far, no others supported
    if(not no_params and not any([i.startswith('bbox') for i in in_product_args])): #there is no boundig box defined
        in_product_args.append(default_bounding_box)
    if(len(in_parameters)>0):
        in_product_args.append("parameters="+",".join(in_parameters))
    query={ 'product_name':in_product_name,\
            'product_args':in_product_args, \
            'grid_type':grid_type,\
            'parameters':[]}
    return query

def fetch_data(d_q):
    #d_q is data_query, a dictionary got from format_query().
    parameters = d_q['parameters']
    print('fetching metadata...')
    model_data = fmi_dsq(d_q['product_name'], args = d_q['product_args'])
    last_data = model_data.data[max(model_data.data.keys())]
    time0 = time.time()
    print('fetching data...')
    last_data.parse(delete = True)
    load_time = time.time() - time0 #seconds

    gathered_data = {}
    latitudes = last_data.latitudes
    longitudes = last_data.longitudes
    time_axis = list(last_data.data.keys())
    layers = last_data.data[min(time_axis)].keys()
    if( d_q['grid_type'] == 'latlon'):
        gathered_data['lat'] = (('lat',), latitudes[:,0])
        gathered_data['lon'] = (('lon',), longitudes[0,:])
    else:
        gathered_data['latitude'] = (('lat','lon'), latitudes)
        gathered_data['longitude'] = (('lat','lon'), longitudes)
    gathered_data['time'] = (('time',), time_axis)

    print("Model data {} acquired successfully. ({:.1f} seconds)".format(d_q['product_name'], load_time))
    print("Available parameters:")
    for v in last_data.data[min(time_axis)][min(layers)].keys():
        print("{} ({})".format(v, last_data.data[min(time_axis)][min(layers)][v]['units']))
    print()

    if(len(parameters) == 0): #No parameters defined, so storing all of them
        parameters = last_data.data[min(time_axis)][min(layers)].keys()
    for var in parameters:
        the_unit = last_data.data[min(time_axis)][min(layers)][var]['units']
        print("Processing: {} ({}), size = {}".format(var, \
                the_unit, \
                last_data.data[min(time_axis)][min(layers)][var]['data'].shape))
        print("\ttimesteps: {} from:{} to {}".format(\
                len(time_axis),
                min(time_axis),
                max(time_axis)
                ))
        new_var = []
        for t in time_axis:
            data = last_data.data[t]
            data = data[min(data.keys())] # take the lowest layer
            new_var.append(xr.DataArray(data[var]['data'], dims = ['lat','lon'], attrs = {'units':the_unit}))
        gathered_data[var] = xr.concat(new_var, dim = xr.DataArray(time_axis, dims = 'time'))


    data_xr = xr.Dataset(gathered_data)
    return data_xr
