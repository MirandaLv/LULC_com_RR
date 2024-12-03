
import pandas as pd
import geopandas as gpd
import os
import rasterio
from shapely.geometry import box
import argparse


def main():

    parser = argparse.ArgumentParser(description='Description of your script.')
    parser.add_argument('input_file', type=str, help='Path to the input shapefile file.')
    parser.add_argument('geotiff_dir', type=str, help='Path to the folder of NAIP images.')
    parser.add_argument('--output_file', type=str, help='Path to the output file.', default='output.shp')
    args = parser.parse_args()

    # Check if input and output directories exist
    if not os.path.exists(args.input_file):
        print(f"Error: Input directory '{args.input_path}' does not exist.")
        return

    # buildings = os.path.join(working_dir, 'data/processed/building_tag.shp')

    gdf = gpd.read_file(args.input_file)

    # Loop through each GeoTIFF file to find matching polygons
    geotiff_files = [os.path.join(args.geotiff_dir, i) for i in os.listdir(args.geotiff_dir) if i.endswith('.tif')]

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
    gdf.to_file(args.output_file)


if __name__ == "__main__":
    main()

"""
in: "/Users/mirandalv/Documents/projects/github/LULC_com_RR/data/buildingfootprint/Mathew/Mathew_buildingfootprint.shp"
dir: "/Users/mirandalv/Documents/projects/github/LULC_com_RR/data/NAIP/Mathew"
out: "/Users/mirandalv/Documents/projects/github/LULC_com_RR/data/processed/Mathew/building_mathew_tiff_delete.shp"
"""


