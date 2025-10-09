import geopandas as gpd
import pandas as pd
import numpy as np
import elapid as ela
import matplotlib as mpl
import matplotlib.pyplot as plt
import contextily as ctx

locations = pd.read_csv(r"/Users/ruby/Documents/locations2.csv")
geometry = ela.xy_to_geoseries(
    x = locations['decimalLongitude'],
    y = locations['decimalLatitude']
)

ariolimax = gpd.GeoDataFrame(locations[["verbatimScientificName", "year"]],
                             geometry=geometry,
                             crs="EPSG:4326")

#print("DataFrame")
#print(locations.head())
#print("\nGeoSeries")
#print(geometry.head())
#print("\nGeoDataFrame")
#print(ariolimax.head())

ariolimax_web = ariolimax.to_crs(epsg=3857)

fig, ax = plt.subplots(figsize=(6,6))

ax = ariolimax_web.plot(
    column="verbatimScientificName",
    categorical=True,
    legend=True,
    markersize=10,
    cmap="tab10",
    alpha=0.8,
    ax=ax
)

ctx.add_basemap(ax, source=ctx.providers.Esri.WorldGrayCanvas)

########################################

california = locations[locations['stateProvince'] == 'California']

geometry = ela.xy_to_geoseries(
    x = california['decimalLongitude'],
    y = california['decimalLatitude']
)

ariolimax_ca = gpd.GeoDataFrame(
    california[['verbatimScientificName', 'year']],
    geometry=geometry,
    crs="EPSG:4326"
)

# convert to Web Mercator
ariolimax_web_ca = ariolimax_ca.to_crs(epsg=3857)

# plot
fig, ax = plt.subplots(figsize=(8,8))
ariolimax_web_ca.plot(
    column='verbatimScientificName',
    categorical=True,
    legend=True,
    markersize=20,
    cmap='tab10',
    alpha=0.8,
    ax=ax
)

# add basemap
ctx.add_basemap(ax, source=ctx.providers.Esri.WorldGrayCanvas)

plt.show()

