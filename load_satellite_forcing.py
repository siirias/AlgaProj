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


conf_dat = ast.literal_eval("".join(open('config.txt').readlines()))
oper_dir = conf_dat['oper_dir']
tiff_file_name = "satellite_tmp.tiff"
savefile_name = "satellite_data.nc"
algae_max_value = 4.0 # This depends on selected dataset.
algae_min_value = 1.0 # as zeroes mark masked values.
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
target_area = '&SUBSET=Lat({},{})&SUBSET=Long({},{})'.\
        format( agt.default_area.lat_min,\
                agt.default_area.lat_max,\
                agt.default_area.lon_min,\
                agt.default_area.lon_max)
target_day = '&SUBSET=time("{}")'.\
        format(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%dT00:00:00Z"))

target_day = '&SUBSET=time("2022-08-02T00:00:00Z")'
wmo_request = "'https://geoserver2.ymparisto.fi/geoserver/eo/wcs?version=2.0.1&request=GetCoverage&coverageId=eo:EO_MR_OLCI_ALGAE&format=image/tiff{}{}'".format(target_area,target_day)

fetch_command = "wget {} -O {}".format(wmo_request, oper_dir+tiff_file_name)
os.system(fetch_command)
sat_database = {}
with rasterio.open(oper_dir+tiff_file_name) as sat_dat:
    mask = sat_dat.dataset_mask()
    algae = sat_dat.read() # for the moment, values 0-4 0 should be same as 1
    algae[algae==0] = 1
    algae = algae-1
    algae = np.array(algae, dtype=float)/(algae_max_value-algae_min_value)
    algae = algae.reshape(mask.shape) #this, to get rid possible extrra dimensions
    sat_database['algae'] = xr.DataArray(algae, dims = ['lat','lon'])
    sat_database['mask'] = xr.DataArray(mask, dims = ['lat','lon'])
    sat_database['lat'] = np.linspace(sat_dat.bounds.top, sat_dat.bounds.bottom, sat_dat.height)
    sat_database['lon'] = np.linspace(sat_dat.bounds.left, sat_dat.bounds.right, sat_dat.width)


data_xr = xr.Dataset(sat_database)
data_xr.to_netcdf(oper_dir + savefile_name, 'w')
print("Saved: {}".format(oper_dir + savefile_name))



