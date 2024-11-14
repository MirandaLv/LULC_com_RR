
import rasterio
import os
import geopandas as gpd
from shapely.geometry import shape
import numpy as np
from rasterio.features import geometry_mask


def create_building_geotiff(landcover_path, shapefile_path, output_path):
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


def reclass_lulc(rst, outrst):

    with rasterio.open(rst) as src:
        data = src.read(1)
        profile = src.profile

    # Create an empty canvas
    reclassified_data = np.zeros_like(data, dtype=np.int32)

    mask_water = np.isin(data, [11, 12, 13, 14, 15])
    mask_roads = np.isin(data, [21, 23, 24, 26])
    mask_structures = np.isin(data, [22, 25, 29, 52])
    mask_turf = np.isin(data, [27, 28])
    mask_ag = np.isin(data, [82, 84])
    mask_other = ~np.isin(data, [11, 12, 13, 14, 15, 21, 23, 24, 26, 22, 25, 29, 52, 27, 28, 82, 84]) # everything else will be classified as Other

    reclassified_data[mask_water] = 1
    reclassified_data[mask_roads] = 2
    reclassified_data[mask_structures] = 3
    reclassified_data[mask_turf] = 4
    reclassified_data[mask_ag] = 5
    reclassified_data[mask_other] = 6

    # Save the reclassified GeoTIFF
    with rasterio.open(outrst, 'w', **profile) as dst:
        dst.write(reclassified_data, 1)




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


# Processing lulc data
general_lulc = ["Water", "Impervious Roads", "Impervious Structures", "Impervious, Other", "Tree Canopy over Impervious",
           "Turf Grass", "Pervious Developed, Other", "Tree Canopy over Turf Grass", "Forest", "Wetlands, Riverine Non-forested"
           "Harvested Forest", "Natural Succession", "Cropland", "Pasture/Hay", "Extractive",
           "Wetlands, Tidal Non-forested", "Tree Canopy, Other", "Wetlands, Terrene Non-forested"]


general_lulc_mapping = {"Water": [11, 12, 13, 14, 15], "Impervious Roads": [21, 23, 24, 26],
                        "Impervious Structures": [22, 25, 29, 52], "Turf": [27, 28],
                        "Agriculture": [82, 84], "Others": []}

















