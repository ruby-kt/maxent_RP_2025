import os
import pandas as pd
import elapid as ela
from sklearn import metrics
import geopandas as gpd
import rasterio
from rasterio.plot import show
from rasterio.windows import from_bounds
import matplotlib.pyplot as plt
import numpy as np

#paths
wc2_folder = "/Users/ruby/Documents/wc2/clipped_research_area/"
locations_file = "/Users/ruby/Documents/locationscsv.csv"

#loading data
locations = pd.read_csv(locations_file)

species_all = locations.dropna(subset=['decimalLongitude', 'decimalLatitude'])

geometry = ela.xy_to_geoseries(
    x=species_all['decimalLongitude'],
    y=species_all['decimalLatitude']
)
species_gdf = gpd.GeoDataFrame(
    species_all[['species', 'year']],
    geometry=geometry,
    crs="EPSG:4326"
)

print("Species records:", species_gdf.shape)

#prep to train
raster_files = [os.path.join(wc2_folder, f) for f in os.listdir(wc2_folder) if f.endswith(".tif")]

background = ela.sample_raster(raster_files[0], count=10_000)

merged = ela.stack_geodataframes(species_gdf, background, add_class_label=True)

merged = merged[merged.geometry.notnull() & merged.is_valid]

annotated = ela.annotate(merged, raster_files, drop_na=True, quiet=True)

x = annotated.drop(columns=['class', 'geometry'])
y = annotated['class']

#train model
model = ela.MaxentModel(transform='cloglog', beta_multiplier=2.0)
model.fit(x, y)

#evaluation
ypred = model.predict(x)
auc = metrics.roc_auc_score(y, ypred)
print("AUC:", auc)
#closer to 1 = good, 0.5 bad sort split

#prediction
output_file = "/Users/ruby/Documents/predicted_suitability_all.tif"
ela.apply_model_to_rasters(
    model,
    raster_files,
    output_path=output_file,
)

#clip to region
corrected_file = "/Users/ruby/Documents/predicted_suitability_all.tif"

west, south, east, north = -140, 30, -110, 60

with rasterio.open(corrected_file) as src:
    window = from_bounds(west, south, east, north, src.transform)
    clipped = src.read(1, window=window)
    transform = src.window_transform(window)
    meta = src.meta.copy()
    meta.update({
        "height": clipped.shape[0],
        "width": clipped.shape[1],
        "transform": transform
    })

clipped_file = "/Users/ruby/Documents/predicted_suitability_all_clipped.tif"
with rasterio.open(clipped_file, "w", **meta) as dst:
    dst.write(clipped, 1)