import xarray as xr
import time
#import algae_tools as agt
import datetime as dt
import os
import numpy as np

import matplotlib as mp
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cmocean as cmo

#conf_dat = agt.conf_dat 
#agt.read_cmd_params()
#oper_dir = conf_dat['oper_dir']
input_dir = 'C:/Data/alga_test/output/'
output_dir = 'C:/Data/alga_test/output/figures/'
start_date = dt.datetime.strptime('2022-06-16','%Y-%m-%d')
end_date = dt.datetime.strptime('2022-07-25','%Y-%m-%d')
current_date = start_date
the_proj = ccrs.PlateCarree()
figure_size = (10,10)
plot_area = [17.0, 30.5, 58.0, 66.0]
color_map = cmo.cm.algae
fig_dpi = 300
close_figures = True

def create_main_map(the_proj):
        fig=plt.figure(figsize=figure_size)
        plt.clf()
        ax = plt.axes(projection=the_proj)
        ax.set_extent(plot_area)
        ax.set_aspect('auto')
        ax.coastlines('10m',zorder=4)
        ax.add_feature(cfeature.NaturalEarthFeature('physical', 'land', '10m',\
                                                edgecolor='face', facecolor='#555560'))
        gl = ax.gridlines(crs=the_proj, draw_labels=True,
                  linewidth=2, color='gray', alpha=0.1, linestyle='-')
        gl.top_labels = False
        gl.right_labels = False
        return fig, ax

while (current_date < end_date):
    step_index = dt.datetime.strftime(current_date,'%Y_%m_%d')
    f_sat = "satellite_data_regridded_e_{}.nc".\
            format(dt.datetime.strftime(current_date,'%Y%m%d'))
    f_init= "start_condition_{}.nc".\
            format(dt.datetime.strftime(current_date,'%Y%m%d'))

    sat_dat = xr.open_dataset(input_dir + f_sat)
    model_dat = xr.open_dataset(input_dir + f_init)
    fig, ax = create_main_map(the_proj)    

    lon = np.array(sat_dat['lon'])
    lat = np.array(sat_dat['lat'])
    data = np.array(sat_dat['algae'])
    lon,lat = np.meshgrid(lon,lat)
    plt.pcolor(lon,lat,data, transform = the_proj, cmap = color_map)
    ax.set_facecolor('#500000')
    plt.colorbar()
    plt.show()
    filename = "sat_{}.png".format(step_index)
    plt.savefig(output_dir + filename\
                            ,dpi=fig_dpi,bbox_inches='tight')
    print("Saved: {} ".format(filename))
    if(close_figures):
        plt.close()

    current_date += dt.timedelta(days=1)

