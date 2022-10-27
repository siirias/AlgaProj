import fmiopendata
from fmiopendata.wfs import download_stored_query as fmi_dsq
import xarray as xr
import time
import ast  # for readign configuration file
import algae_tools as agt

conf_dat = ast.literal_eval("".join(open('config.txt').readlines()))
oper_dir = conf_dat['oper_dir']
savefile_name = "meteor_data.nc"
product_name = "fmi::forecast::harmonie::surface::grid"
"""
List of available products: https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=describeStoredQueries

Products that might be useful:
    fmi::forecast::harmonie::surface::grid
    ecmwf::forecast::surface::grid
    fmi::forecast::hbm::grid
    fmi::forecast::wam::grid

"""
the_query = agt.format_query(product_name)
data_xr = agt.fetch_data(the_query)

data_xr.to_netcdf(oper_dir + savefile_name, 'w')
print("Saved: {}".format(oper_dir + savefile_name))
