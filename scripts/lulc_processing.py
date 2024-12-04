
import rasterio
import os
import geopandas as gpd
from shapely.geometry import shape
import numpy as np
from rasterio.features import geometry_mask


def create_building_geotiff(landcover_path, shapefile_p, output_path, key_name="predict"):

    if isinstance(shapefile_p, gpd.GeoDataFrame):
        gdf = shapefile_p
    elif os.path.isfile(shapefile_p) and shapefile_p.endswith("shp"):
        # Read the shapefile
        gdf = gpd.read_file(shapefile_p)
    else:
        raise TypeError("The input of building file should be either a GeoDataFrame or shapefile")

    # Open the landcover GeoTIFF
    with rasterio.open(landcover_path) as src:
        profile = src.profile  # Get the profile for the output GeoTIFF
        landcover_data = src.read(1)  # Read the data as a 2D array (assuming single-band landcover)
        transform = src.transform

    # Create an empty array to hold the output classification
    classification = np.zeros_like(landcover_data, dtype=np.uint8)  # 0 by default

    # Loop through the geometries in the shapefile

    # Process commercial buildings
    commercial_geometries = gdf[gdf[key_name] == 'commercial_industry']['geometry']

    if not commercial_geometries.empty:
        commercial_mask = geometry_mask(
            commercial_geometries,
            transform=transform,
            invert=True,
            out_shape=landcover_data.shape
        )
        classification[commercial_mask] = 1

    # Process residential buildings
    residential_geometries = gdf[gdf[key_name] == 'residential']['geometry']
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



def combine_lulc_building(lulc_path, building_path, outpath):

    with rasterio.open(lulc_path) as src1:
        lulc_data = src1.read(1)
        profile = src1.profile  # Copy profile for output file
        profile.update(dtype=rasterio.uint8)  # Ensure output data type is set correctly


    with rasterio.open(building_path) as src2:
        building_data = src2.read(1)

    # Create a canvas
    output_data = np.where(np.isin(lulc_data, [1, 2, 3, 4, 5, 6]), lulc_data, 0) # make sure all has value

    # Reclassify 'structure' in lulc to either 'residential building' or 'commercial'
    # based on the values in building raster (1=commercial_industry, 2=residential)
    structure_mask = lulc_data == 3
    output_data[structure_mask & (building_data == 1)] = 7  # 7 represents residential in the new output
    output_data[structure_mask & (building_data == 2)] = 8  # 8 represents commercial in the new output

    # Write the output GeoTIFF
    with rasterio.open(outpath, 'w', **profile) as dst:
        dst.write(output_data, 1)


def combine_data(lulc_path, building_path, outpath):

    with rasterio.open(building_path) as src1:
        building_data = src1.read(1)
        profile = src1.profile
        profile.update(dtype=rasterio.uint8)  # Ensure output data type is set correctly

    with rasterio.open(lulc_path) as src2:
        lulc_data = src2.read(1)

    # Initialize output data array filled with nodata value if defined, otherwise zeros
    output_data = np.full_like(building_data, fill_value=0, dtype=np.uint8)

    # Assign values for residential and commercial from the first layer
    output_data[building_data == 1] = 1  # 1 for commercial_industry
    output_data[building_data == 2] = 2  # 2 for residential

    # Create a mask for areas not assigned in output_data
    unassigned_mask = (building_data != 1) & (building_data != 2)

    # Assign values from the lulc layer
    output_data[(unassigned_mask) & (lulc_data == 1)] = 3  # Water
    output_data[(unassigned_mask) & (lulc_data == 2)] = 4  # Road
    output_data[(unassigned_mask) & (lulc_data == 3)] = 5  # Structure
    output_data[(unassigned_mask) & (lulc_data == 4)] = 6  # Turf
    output_data[(unassigned_mask) & (lulc_data == 5)] = 7  # Ag
    output_data[(unassigned_mask) & (lulc_data == 6)] = 8  # Other

    # Write the output GeoTIFF
    with rasterio.open(outpath, 'w', **profile) as dst:
        dst.write(output_data, 1)



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

















