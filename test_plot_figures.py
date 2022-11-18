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
start_date = dt.datetime.strptime('2019-06-05','%Y-%m-%d')
end_date = dt.datetime.strptime('2019-08-30','%Y-%m-%d')
current_date = start_date
the_proj = ccrs.PlateCarree()
figure_size = (10,10)
plot_area = [17.0, 30.5, 59.0, 66.0]
color_map = cmo.cm.algae
color_map_rel = cmo.cm.rain
fig_dpi = 300
close_figures = True
alg_min = 0.0
alg_max = 1.0

plot_sat_figs = True
plot_init_figs = True
plot_init_reliable_figs = True
plot_init_mosaic_figs = True

def create_main_map(the_proj, fig = None, ax = None):
        if(not ax):
            fig=plt.figure(figsize=figure_size)
            plt.clf()
            ax = plt.axes(projection=the_proj)
        else:
            ax.projection = the_proj
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
    f_ship= "ship_data_e_{}.nc".\
            format(dt.datetime.strftime(current_date,'%Y%m%d'))
    f_init= "start_condition_{}.nc".\
            format(dt.datetime.strftime(current_date,'%Y%m%d'))
    f_init_prev= "start_condition_{}.nc".\
            format(dt.datetime.strftime(current_date-dt.timedelta(days=1),'%Y%m%d'))

    sat_dat = xr.open_dataset(input_dir + f_sat)
    ship_dat = xr.open_dataset(input_dir + f_ship)
    model_dat = xr.open_dataset(input_dir + f_init)
    prev_model_dat = xr.open_dataset(input_dir + f_init_prev)
    lon = np.array(sat_dat['lon'])
    lat = np.array(sat_dat['lat'])
    sat_algae = np.array(sat_dat['algae'])
    ship_algae = np.array(ship_dat['algae'])
    init_algae = np.array(model_dat['algae'])
    prev_init_algae = np.array(prev_model_dat['algae'])
    init_reliab = np.array(model_dat['reliability'])
    lon,lat = np.meshgrid(lon,lat)
    if(plot_sat_figs):
        fig, ax = create_main_map(the_proj)    
        plt.pcolor(lon,lat,sat_algae, transform = the_proj, cmap = color_map\
                ,vmin = alg_min, vmax = alg_max)
        ax.set_facecolor('#500000')
        plt.colorbar()
        plt.title("Satellite product {}".format(step_index))
        plt.show()
        filename = "sat_{}.png".format(step_index)
        plt.savefig(output_dir + filename\
                                ,dpi=fig_dpi,bbox_inches='tight')
        print("Saved: {} ".format(filename))
        if(close_figures):
            plt.close()
    if(plot_init_figs):
        fig, ax = create_main_map(the_proj)    
        plt.pcolor(lon,lat,init_algae, transform = the_proj, cmap = color_map\
                ,vmin = alg_min, vmax = alg_max)
        ax.set_facecolor('#500000')
        plt.colorbar()
        plt.title("initial field {}".format(step_index))
        plt.show()
        filename = "init_{}.png".format(step_index)
        plt.savefig(output_dir + filename\
                                ,dpi=fig_dpi,bbox_inches='tight')
        print("Saved: {} ".format(filename))
        if(close_figures):
            plt.close()
    if(plot_init_reliable_figs):
        fig, axes = plt.subplots(nrows =1, ncols = 2,\
                subplot_kw = {'projection':the_proj}, \
                figsize = (figure_size[0]*2, figure_size[1]))
        ax = axes[0]
        plt.sca(ax)
        create_main_map(the_proj,fig, ax)    
        plot_obj = ax.pcolor(lon,lat,init_algae, \
                transform = the_proj, cmap = color_map\
                ,vmin = alg_min, vmax = alg_max)
        ax.set_facecolor('#500000')
        plt.colorbar(mappable = plot_obj)
        plt.title("initial field {}".format(step_index))


        ax = axes[1]
        create_main_map(the_proj,fig, ax)    
        plt.sca(ax)
        plot_obj = plt.pcolor(lon,lat,init_reliab, \
                transform = the_proj, cmap = color_map_rel\
                ,vmin = alg_min, vmax = alg_max)
        ax.set_facecolor('#500000')
        plt.colorbar(mappable = plot_obj)
        plt.title("reliability {}".format(step_index))

        plt.show()
        filename = "init_rel_{}.png".format(step_index)
        plt.savefig(output_dir + filename\
                                ,dpi=fig_dpi,bbox_inches='tight')
        print("Saved: {} ".format(filename))
        if(close_figures):
            plt.close()

    if(plot_init_mosaic_figs):
        fig, axes = plt.subplots(nrows =2, ncols = 2,\
                subplot_kw = {'projection':the_proj}, \
                figsize = (figure_size[0], figure_size[1]))
        axes = list(np.reshape(axes,(4)))
        ax = axes[0]
        plt.sca(ax)
        create_main_map(the_proj,fig, ax)    
        plot_obj = ax.pcolor(lon,lat,init_algae,\
                transform = the_proj, cmap = color_map\
                ,vmin = alg_min, vmax = alg_max)
        ax.set_facecolor('#500000')
        plt.colorbar(mappable = plot_obj)
        plt.title("initial field {}".format(step_index))


        ax = axes[1]
        create_main_map(the_proj,fig, ax)    
        plt.sca(ax)
        plot_obj = plt.pcolor(lon,lat,sat_algae,\
                transform = the_proj, cmap = color_map\
                ,vmin = alg_min, vmax = alg_max)
        ax.set_facecolor('#500000')
        plt.colorbar(mappable = plot_obj)
        plt.title("satellite {}".format(step_index))

        ax = axes[2]
        create_main_map(the_proj,fig, ax)    
        plt.sca(ax)
        plot_obj = plt.pcolor(lon,lat,ship_algae,
                transform = the_proj, cmap = color_map\
                ,vmin = alg_min, vmax = alg_max)
        ax.set_facecolor('#500000')
        plt.colorbar(mappable = plot_obj)
        plt.title("ship {}".format(step_index))

        ax = axes[3]
        create_main_map(the_proj,fig, ax)    
        plt.sca(ax)
        plot_obj = plt.pcolor(lon,lat,prev_init_algae, 
                transform = the_proj, cmap = color_map\
                ,vmin = alg_min, vmax = alg_max)
        ax.set_facecolor('#500000')
        plt.colorbar(mappable = plot_obj)
        plt.title("previous field {}".format(step_index))


        plt.show()
        filename = "init_mosaic_{}.png".format(step_index)
        plt.savefig(output_dir + filename\
                                ,dpi=fig_dpi,bbox_inches='tight')
        print("Saved: {} ".format(filename))
        if(close_figures):
            plt.close()

    current_date += dt.timedelta(days=1)

