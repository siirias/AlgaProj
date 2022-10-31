import fmiopendata
from fmiopendata.wfs import download_stored_query as fmi_dsq
import xarray as xr
import time
import ast  # for readign configuration file
import algae_tools as agt

conf_dat = ast.literal_eval("".join(open('config.txt').readlines()))
oper_dir = conf_dat['oper_dir']
savefile_name = "hydrodyn_data.nc"
#product_name = "fmi::forecast::hbm::grid"
product_name = "fmi::forecast::hbm::grid"
"""
List of available products: https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=describeStoredQueries

Products that might be useful:
    fmi::forecast::harmonie::surface::grid
    ecmwf::forecast::surface::grid
    fmi::forecast::hbm::grid
    fmi::forecast::wam::grid

Parameters in ecmwf:
    "Pressure","GeopHeight","Temperature","DewPoint","Humidity","WindDirection",
    "WindSpeedMS","WindUMS","WindVMS","PrecipitationAmount","TotalCloudCover",
    "LowCloudCover","MediumCloudCover","HighCloudCover","RadiationGlobal",
    "RadiationGlobalAccumulation","RadiationNetSurfaceLWAccumulation",
    "RadiationNetSurfaceSWAccumulation"," RadiationSWAccumulation","Visibility",
    "WindGust","Cape"

Parameters in hbm/hydrodyn
"TemperatureSea", "Salinity", "CurrentSpeed", "CurrentDirection", "SeaWaterVelocityW", #"SeaWaterVelocityU", "SeaWaterVelocityV"

parameters in wam
"SigWaveHeight", "SigWavePeriod", "WaveDirection"



"""
the_query={}

#parameters =["TemperatureSea","Salinity","SeaWaterVelocityU","SeaWaterVelocityV"]
parameters =["TemperatureSea", "Salinity", "CurrentSpeed", "CurrentDirection"]
data_xr_list = []
for p in parameters:
    the_query = agt.format_query(product_name, [], in_parameters = [p])
    data_xr_list.append(agt.fetch_data(the_query))

data_xr = xr.merge(data_xr_list)
data_xr.to_netcdf(oper_dir + savefile_name, 'w')
print("Saved: {}".format(oper_dir + savefile_name))


