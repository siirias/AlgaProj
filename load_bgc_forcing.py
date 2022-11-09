import fmiopendata
from fmiopendata.wfs import download_stored_query as fmi_dsq
import xarray as xr
import time
import ast  # for readign configuration file
import algae_tools as agt
import os
import datetime as dt

conf_dat = agt.conf_dat
agt.read_cmd_params()
oper_dir = conf_dat['oper_dir']
savefile_name = "bgc_data.nc"
motu_command_base = 'python -m motuclient --motu https://nrt.cmems-du.eu/motu-web/Motu --service-id {:} --product-id {:} --longitude-min {:} --longitude-max {:} --latitude-min {:} --latitude-max {:} --date-min "{}" --date-max {} --depth-min 1 --depth-max 20 --variable chl --variable o2 --out-dir {} --out-name {} --user {} --pwd {}'


"""
Example motu command:

python -m motuclient --motu https://nrt.cmems-du.eu/motu-web/Motu 
--service-id BALTICSEA_ANALYSISFORECAST_BGC_003_007-TDS 
--product-id dataset-bal-analysis-forecast-bio-dailymeans 
--longitude-min 17.0416 --longitude-max 30.2087 
--latitude-min 58.0083 --latitude-max 65.891 
--date-min "2022-10-31 12:00:00" --date-max "2022-11-05 12:00:00" 
--depth-min 1 --depth-max 20 
--variable chl --variable o2 
--out-dir . 
--out-name koe.nc 
--user X --pwd Y
"""
forecast_length = agt.model_parameters['forecast_length']
motu_service_id = 'BALTICSEA_ANALYSISFORECAST_BGC_003_007-TDS'
motu_product_id = 'dataset-bal-analysis-forecast-bio-dailymeans'
lon_min = agt.default_area.lon_min
lat_min = agt.default_area.lat_min
lon_max = agt.default_area.lon_max
lat_max = agt.default_area.lat_max
req_time = agt.model_parameters['forecast_time']
dat_min = dt.datetime.strftime(req_time,'%Y-%m-%d 00:00:00')
dat_max = dt.datetime.strftime(req_time+\
        dt.timedelta(hours=forecast_length),'%Y-%m-%d 00:00:00')

motu_command = motu_command_base.format(
        motu_service_id,
        motu_product_id,
        lon_min, lon_max, lat_min, lat_max,
        dat_min, dat_max,
        oper_dir,
        savefile_name,
        conf_dat['copernicus_login'],
        conf_dat['copernicus_pw']
        )
os.system(motu_command)
print(agt.model_parameters)
