import fmiopendata
from fmiopendata.wfs import download_stored_query as fmi_dsq
import ast  # for readign configuration file
import numpy as np
import xarray as xr
import time
import datetime as dt
import sys
import getopt  # for interpreting command-line parameters

"""
The purpose of this script is to provide functions needed in several scripts
that will consist of the alage product.

When imported, finds config.txt (must be in run directory) 
and model_parameters.txt (found on directory defined in config.txt)
loads parameter lists in conf_dat, model_parameters, and default_area

Currently in:
    class ModelArea: holds the limits and landmask of target model area. if found,
                        loaded from netcdf pointed in gridtemplate in default_area
    
    format_query(): Returns a dictionary that can be used for fetch_data 
    fetch_data(DataQuery): Fetches data from fmi opendata system, and returns xarray Dataset 
                            that can be saved as netCDF
    read_cmd_params(): interpretes set of commandline parameters into model_parameters
"""
class ModelArea:
    def __init__(self):
        self.lat_max = 66.0
        self.lat_min = 59.0
        self.lon_max = 30.0
        self.lon_min = 16.0
        self.grid = None
    def bb(self):
        return 'bbox={},{},{},{}'.format(self.lon_min,self.lat_min,self.lon_max,self.lat_max)



default_area = ModelArea()
conf_dat = ast.literal_eval("".join(open('config.txt').readlines()))
conf_dir = conf_dat['config_dir']
model_parameters = ast.literal_eval("".join(open(conf_dir + 'model_parameters.txt').readlines()))
if(not 'forecast_time' in model_parameters.keys() or \
        model_parameters['forecast_time'] == ''): #no time set, so today
    t_tmp = dt.datetime.now()
    model_parameters['forecast_time'] = dt.datetime(t_tmp.year, t_tmp.month, t_tmp.day)
else: #parameters have an actual date, so let's interprete
     model_parameters['forecast_time'] = \
             dt.datetime.strptime(model_parameters['forecast_time'],'%Y-%m-%d')
        

if 'grid_template' in model_parameters.keys():
    with xr.open_dataset(conf_dir + model_parameters['grid_template']) as the_grid:
        default_area.grid = the_grid
        default_area.lat_max = float(np.max(the_grid.lat))
        default_area.lat_min = float(np.min(the_grid.lat))
        default_area.lon_max = float(np.max(the_grid.lon))
        default_area.lon_min = float(np.min(the_grid.lon))


def read_cmd_params():
    opts, args = getopt.getopt(sys.argv[1:],\
            "ht:l:",\
            ["help","starttime=","length="])
    for opt, arg in opts:
        if opt in ("-h","--help"):
            print("tbd")
            sys.exit()
        elif opt in ("-t", "--starttime"):
            model_parameters['forecast_time'] = \
                     dt.datetime.strptime(arg, '%Y-%m-%d')
        elif opt in ("-l", "--length"):
            model_parameters["forecast_length"] = int(arg)

def format_query(in_product_name, in_product_args=[], in_parameters=[],*, no_params=False):
    grid_type = 'latlon'  #so far, no others supported
    if(not no_params and not any([i.startswith('bbox') for i in in_product_args])): #there is no boundig box defined
        in_product_args.append(default_area.bb())
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
    data_xr = add_meta_data(data_xr)
    return data_xr

def add_meta_data(the_dataset):
    # adds coordinate units.
    the_dataset.lat.attrs['units'] = 'degrees_north'
    the_dataset.lon.attrs['units'] = 'degrees_east'
    return the_dataset
