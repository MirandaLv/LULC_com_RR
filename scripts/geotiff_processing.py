
import pandas as pd
import geopandas as gpd
import os
import rasterio
from shapely.geometry import box


def main(input_path, output_path):
    # Check if input and output directories exist
    if not os.path.exists(input_path):
        print(f"Error: Input directory '{input_path}' does not exist.")
        return

    if os.path.exists(output_path):
        print(f"Error: Output directory '{output_path}' exist.")
        return

    # buildings = os.path.join(working_dir, 'data/processed/building_tag.shp')

    gdf = gpd.read_file(input_path)

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

    gdf = gdf[gdf['geotiff'].notnull()]  # remove polygons that has no geotiff data coverage
    gdf.to_file(output_path)


if __name__ == "__main__":
    working_dir = os.path.abspath('../')
    naip_dir = os.path.join(working_dir, 'data/NAIP')
    geotiff_files = [os.path.join(naip_dir, i) for i in os.listdir(naip_dir) if i.endswith('.tif')]
    inpath = os.path.join(working_dir, 'data/processed/building_tag.shp')
    outpath = os.path.join(working_dir, 'data/processed/building_mathew_tiff.shp')
    main(inpath, outpath)

