import fmiopendata
from fmiopendata.wfs import download_stored_query as fmi_dsq
import xarray as xr
import time
import ast  # for readign configuration file
import algae_tools as agt
import rasterio
import datetime as dt
import os
import numpy as np


conf_dat = agt.conf_dat 
oper_dir = conf_dat['oper_dir']
agt.read_cmd_params()
tiff_file_name = "satellite_tmp.tiff"
algae_max_value = 4.0 # This depends on selected dataset.
algae_min_value = 1.0 # as zeroes mark masked values.
max_download_attempts = 5  #how many times retry, if file fetch fails
"""
Example:
https://geoserver2.ymparisto.fi/geoserver/eo/wcs
?version=2.0.1
&request=GetCoverage&coverageId=eo:EO_MR_OLCI_ALGAE
&SUBSET=Lat(61.01847,61.33005)
&SUBSET=Long(20.77862,21.50516)
&format=image/tiff
&SUBSET=time("2022-07-20T00:00:00Z")
"""
#products: 
## MER_FSG_L3_rp2017_chla  a-chlorofylli, tätä vaan vuoteen 2011
## EO_MR_OLCI_ALGAE Pintalevätulkinta (60 m)
#target_product = "EO_MR_OLCI_ALGAE"
if( 'product' in agt.model_parameters.keys() and agt.model_parameters['product'] != ''):
    target_product = agt.model_parameters['product']
else:
    target_product = "EO_MR_OLCI_ALGAE"
if( 'out_file' in agt.model_parameters.keys() and agt.model_parameters['out_file'] != ''):
    savefile_name = agt.model_parameters['out_file']
else:
    savefile_name = "satellite_data.nc"

target_area = '&SUBSET=Lat({},{})&SUBSET=Long({},{})'.\
        format( agt.default_area.lat_min,\
                agt.default_area.lat_max,\
                agt.default_area.lon_min,\
                agt.default_area.lon_max)
if(agt.model_parameters["forecast_time"] != ''):
    target_day = '&SUBSET=time("{}")'.\
        format(dt.datetime.strftime(agt.model_parameters["forecast_time"], "%Y-%m-%dT00:00:00Z"))
else:
    target_day = '&SUBSET=time("{}")'.\
        format(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%dT00:00:00Z"))

#target_day = '&SUBSET=time("2022-07-02T00:00:00Z")'
wmo_request = "'https://geoserver2.ymparisto.fi/geoserver/eo/wcs?version=2.0.1&request=GetCoverage&coverageId=eo:{}&format=image/tiff{}{}'".format(target_product, target_area,target_day)

fetch_command = "wget {} -O {}".format(wmo_request, oper_dir+tiff_file_name)
tries = 0
success = False
if('debug' in agt.model_parameters.keys()):
    max_download_attempts = -1
    success = True
while (tries < max_download_attempts and not success):
    os.system(fetch_command)
    if(os.path.isfile(oper_dir+tiff_file_name)):
            if(os.path.getsize(oper_dir+tiff_file_name)>0):
                success = True
    if(not success):
        print('retrying...')
    tries +=1
if(not success):
    print("Failed to fetch satellite data")
    exit(0)

sat_database = {}
with rasterio.open(oper_dir+tiff_file_name) as sat_dat:
    mask = sat_dat.dataset_mask()
    algae = sat_dat.read() # for the moment, values 0-4 0 should be same as 1
    if(target_product == 'EO_MR_OLCI_ALGAE'):
#        algae[algae==0] = -1 
        algae = algae-1
        algae = np.array(algae, dtype=float)/(algae_max_value-algae_min_value)
    else:
        algae = np.array(algae, dtype=float)
            
    algae = algae.reshape(mask.shape) #this, to get rid possible extrra dimensions
    sat_database['mask'] = xr.DataArray(mask, dims = ['lat','lon'])
    sat_database['algae'] = xr.DataArray(algae, dims = ['lat','lon'])
    sat_database['algae'] =  sat_database['algae'].where(sat_database['mask']>10)
    sat_database['lat'] = np.linspace(sat_dat.bounds.top, sat_dat.bounds.bottom, sat_dat.height)
    sat_database['lon'] = np.linspace(sat_dat.bounds.left, sat_dat.bounds.right, sat_dat.width)

data_xr = xr.Dataset(sat_database)
data_xr = agt.add_meta_data(data_xr)
data_xr.to_netcdf(oper_dir + savefile_name, 'w')
print("Saved: {}".format(oper_dir + savefile_name))



