
import rasterio
import os
import geopandas as gpd
from shapely.geometry import shape
import numpy as np
from rasterio.features import geometry_mask

working_dir = os.path.abspath('../')
# data_path = os.path.join(working_dir, 'data/lulc/math_51115_landcover_2018.tif')
lulc_path = os.path.join(working_dir, 'data/lulc/math_51115_lu_2018_26918.tif')
building_path = os.path.join(working_dir, 'prediction/mathew_prediction.shp')
building_rst_path = os.path.join(working_dir, 'prediction/mathew_building_rst.tiff')


def create_classification_geotiff(landcover_path, shapefile_path, output_path):
    # Open the landcover GeoTIFF
    with rasterio.open(landcover_path) as src:
        profile = src.profile  # Get the profile for the output GeoTIFF
        landcover_data = src.read(1)  # Read the data as a 2D array (assuming single-band landcover)
        transform = src.transform

    # Read the shapefile
    gdf = gpd.read_file(shapefile_path)

    # Create an empty array to hold the output classification
    classification = np.zeros_like(landcover_data, dtype=np.uint8)  # 0 by default

    # Loop through the geometries in the shapefile

    # Process commercial buildings
    commercial_geometries = gdf[gdf['predict'] == 'commercial_industry']['geometry']

    if not commercial_geometries.empty:
        commercial_mask = geometry_mask(
            commercial_geometries,
            transform=transform,
            invert=True,
            out_shape=landcover_data.shape
        )
        classification[commercial_mask] = 1

    # Process residential buildings
    residential_geometries = gdf[gdf['predict'] == 'residential']['geometry']
    if not residential_geometries.empty:
        residential_mask = geometry_mask(
            residential_geometries,
            transform=transform,
            invert=True,
            out_shape=landcover_data.shape
        )
        classification[residential_mask] = 2

    # Write the new GeoTIFF
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(classification, 1)





# lc_mapping = {1: "Water", 2: "Emergent wetland", 3: "Tree canopy", 4: "Scrub\Shrub",
#               5: "Herbaceous", 6: "Barren", 7: "Structure", 8: "Other impervious",
#               9: "Roads", 10: "Tree Canopy over Structures", 11: "Tree Canopy over Other Impervious",
#               12: "Tree Canopy over Roads"}


"""
water: 11, 13, 14, 15 -> water 1
imperPaved: 21, 23, 24, 26 -> paved 2
structureDev: 22, 25, 29, 52 -> commercial and residential -> structure 3
agriculture: 82, 84 -> agriculture 4
N/A: 41, 42, 55, 62, 64, 65, 75, 91, 92, 94, 95 -> Other 5
turf_grass: 27, 28 -> turf 6
"""

"""
structure: commercial and residential -> 1, 2, 0
"""

# Processing building data
is_building_process = False

if is_building_process:
    create_classification_geotiff(lulc_path, building_path, building_rst_path)

# Processing lulc data
general_lulc_mapping = {"Water": [11, 13, 14, 15], "Impervious Roads": []}




















