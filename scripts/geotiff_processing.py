
import pandas as pd
import geopandas as gpd
import os
import rasterio
from shapely.geometry import box

working_dir = os.path.abspath('../')

naip_dir = os.path.join(working_dir, 'data/NAIP')
buildings = os.path.join(working_dir, 'data/processed/building_tag.shp')

geotiff_files = [os.path.join(naip_dir, i) for i in os.listdir(naip_dir) if i.endswith('.tif')]
gdf = gpd.read_file(buildings)

# Loop through each GeoTIFF file to find matching polygons
for geotiff_path in geotiff_files:
    # Open the GeoTIFF file and get its bounds
    with rasterio.open(geotiff_path) as src:
        geotiff_bounds = box(*src.bounds)  # Creates a bounding box geometry for the GeoTIFF
        geotiff_name = geotiff_path.split('/')[-1]  # Extract just the file name

    # Select polygons that intersect with the current GeoTIFF bounding box
    matching_buildings = gdf[gdf.within(geotiff_bounds)]

    # Update the 'geotiff_name' column for matching polygons
    gdf.loc[matching_buildings.index, "geotiff"] = geotiff_name

gdf = gdf[gdf['geotiff'].notnull()] # remove polygons that has no geotiff data coverage
# Save the updated GeoDataFrame back to a new shapefile
gdf.to_file(os.path.join(working_dir, 'data/processed/building_tag_tiff.shp'))