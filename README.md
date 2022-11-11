An attemt for rough estimate of Algae development on given area.
ROUGH PLAN:

Will need as input at least:
	surface-layer currents for the period of forecast
	model fields for sun/wind/mixing
	in-situ/satellite measurements of current algae status

Pieces in this package will consist of:
	-part that combines available data on current biomass into gridded data
	-approximates how mixed the top layer/how much of the mass is visible on surface (based on wind history?)
	-Part that using currents information and calculated biomass, approximates movement and furture situation
	-part that approximates algae multiplication factor based on at least sun and temperature?


REQUIREMENTS SO FAR:

 - wget  for aquiring satellite
 - scp   for aquiring ship data
 - cdo   for reshaping downloaded netcdf's
channels:
 - conda-forge
 
 
dependencies:
- numpy
- pandas
- xarray
- scipy
- netcdf4

- rasterio for satellite data downloading
- motu client for bgc data loading: https://help.marine.copernicus.eu/en/articles/4796533-what-are-the-motu-client-motuclient-and-python-requirements
- imageio for writing figures with the test functions
- fmiopendata: https://github.com/pnuu/fmiopendata  for downloading fmi data
