import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.ops import unary_union

states = gpd.read_file("/Users/ruby/Documents/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp")

research_states = states[states['name'].isin(['California', 'Oregon', 'Washington', 'Alaska', 'British Columbia'])]

research_area = unary_union(research_states.geometry)

#folders
wc2_folder = "/Users/ruby/Documents/wc2/"
clipped_folder = "/Users/ruby/Documents/wc2/clipped_research_area/"
os.makedirs(clipped_folder, exist_ok=True)

wc2_files = [f for f in os.listdir(wc2_folder) if f.endswith(".tif")]

for fname in wc2_files:
    raster_path = os.path.join(wc2_folder, fname)
    clipped_path = os.path.join(clipped_folder, fname)

    with rasterio.open(raster_path) as src:
        out_image, out_transform = mask(src, [research_area], crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        with rasterio.open(clipped_path, "w", **out_meta) as dest:
            dest.write(out_image)
