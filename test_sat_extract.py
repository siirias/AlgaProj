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
import imageio as iio
"""
This is a helper function, which just downloads and converts geotiffs
from satellite data into jpges for easier viewing of series
"""

conf_dat = ast.literal_eval("".join(open('config.txt').readlines()))
oper_dir = conf_dat['oper_dir']
algae_max_value = 4.0 # This depends on selected dataset.
algae_min_value = 1.0
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

day = dt.datetime(2022,7,1) 
for i in range(90):

    target_day = '&SUBSET=time("{}")'.format((dt.datetime.strftime(day, "%Y-%m-%dT00:00:00Z")))
    wmo_request = "'https://geoserver2.ymparisto.fi/geoserver/eo/wcs?version=2.0.1&request=GetCoverage&coverageId=eo:EO_MR_OLCI_ALGAE&format=image/tiff{}{}'".format(target_area,target_day)

    tiff_file_name = "satellite_tmp.tiff"
    fetch_command = "wget {} -O {}".format(wmo_request, oper_dir+tiff_file_name)
    os.system(fetch_command)
        
    with rasterio.open(oper_dir+tiff_file_name) as sat_dat:
        mask = sat_dat.dataset_mask()
        algae = sat_dat.read()
        algae[algae == 0] = 1
        algae = algae -1
        algae = (np.array(algae, dtype=float)/(algae_max_value-algae_min_value))*255.0
        algae = algae.reshape(mask.shape) #this, to get rid possible extra dimensions
        filename = 'sat_frame{}.jpg'.format(dt.datetime.strftime(day, "%Y%m%d"))
        iio.imwrite(oper_dir+filename, algae)       
        mask = np.abs(mask-255)
        maskfilename = 'mask_frame{}.jpg'.format(dt.datetime.strftime(day, "%Y%m%d"))
        iio.imwrite(oper_dir+maskfilename, np.stack((mask,np.zeros(mask.shape), np.zeros(mask.shape)),2))        

    day = day + dt.timedelta(days = 1)
