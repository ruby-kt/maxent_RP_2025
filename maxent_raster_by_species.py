import os
import pandas as pd
import elapid as ela
from sklearn import metrics
import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds

# paths
wc2_folder = "/Users/ruby/Documents/wc2/clipped_research_area/"
locations_folder = "/Users/ruby/Documents/filtered_locations_ariolimax/"
output_folder = "/Users/ruby/Documents/ariolimax_rasters/"

os.makedirs(output_folder, exist_ok=True)

# raster data
raster_files = [os.path.join(wc2_folder, f) for f in os.listdir(wc2_folder) if f.endswith(".tif")]
background = ela.sample_raster(raster_files[0], count=10_000)

# bounding box (remove if you don’t want clipping)
west, south, east, north = -140, 30, -110, 60

# store results
auc_scores = {}

# loop through all CSVs
for file in os.listdir(locations_folder):
    if file.endswith(".csv"):
        locations_file = os.path.join(locations_folder, file)

        # species name from filename
        species_name = file.replace("locations_", "").replace(".csv", "")
        print(f"\n--- Processing {species_name} ---")

        # load data
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

        # prep training data
        merged = ela.stack_geodataframes(species_gdf, background, add_class_label=True)
        merged = merged[merged.geometry.notnull() & merged.is_valid]
        annotated = ela.annotate(merged, raster_files, drop_na=True, quiet=True)

        x = annotated.drop(columns=['class', 'geometry'])
        y = annotated['class']

        # train model
        model = ela.MaxentModel(transform='cloglog', beta_multiplier=2.0)
        model.fit(x, y)

        # evaluation
        ypred = model.predict(x)
        auc = metrics.roc_auc_score(y, ypred)
        auc_scores[species_name] = auc
        print(f"AUC for {species_name}: {auc:.3f}")

        # prediction file
        output_file = os.path.join(output_folder, f"predicted_suitability_{species_name}.tif")
        ela.apply_model_to_rasters(model, raster_files, output_path=output_file)

        # clip
        clipped_file = os.path.join(output_folder, f"predicted_suitability_{species_name}_clipped.tif")
        with rasterio.open(output_file) as src:
            window = from_bounds(west, south, east, north, src.transform)
            clipped = src.read(1, window=window)
            transform = src.window_transform(window)
            meta = src.meta.copy()
            meta.update({
                "height": clipped.shape[0],
                "width": clipped.shape[1],
                "transform": transform
            })

        with rasterio.open(clipped_file, "w", **meta) as dst:
            dst.write(clipped, 1)

        print(f"Saved clipped raster: {clipped_file}")

# save AUC results to file
auc_file = os.path.join(output_folder, "auc_scores.txt")
with open(auc_file, "w") as f:
    for species, score in auc_scores.items():
        f.write(f"{species}: {score:.3f}\n")

print(f"\nAUC scores saved to {auc_file}")
