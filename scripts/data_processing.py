
# processing zoning data and lulc data to extract the land with label

import pandas as pd
import geopandas as gpd
import rasterio
import os
import numpy as np
from rasterstats import zonal_stats
from shapely.geometry import LineString
import ast


working_dir = os.path.abspath('../')

york_zone = os.path.join(working_dir, 'data/Zoning_York/zoing_york_26918.shp')
jcc_lulc = os.path.join(working_dir, 'data/JCC_Land_Use/jcc_lu_26918.shp')
buildings = os.path.join(working_dir, 'data/buildingfootprint/VACounty_building_jcc_york_proj.shp')

york_gdf = gpd.read_file(york_zone)
jcc_gdf = gpd.read_file(jcc_lulc)
bd_gdf = gpd.read_file(buildings)

# all_zones_york = {'RMF': 'multifamily residential',
#              'RR': 'rural residential',
#              'R33': 'low density single family',
#              'x': 'unknown',
#              'NB': 'neighbor business',
#              'WCI': 'water oriented commercial and industry',
#              'EO': 'eco opportunity',
#              'R13': 'high density single family residential',
#              'LB': 'limited business',
#              'R7': 'manufactured home subdivision',
#              'GB': 'general business',
#              'YVA': 'yorktown village activity',
#              'IL': 'limited industry',
#              'RC': 'resource conservation',
#              'PD': 'planned development',
#              'R20': 'medium density single family',
#              'IG': 'general industry'}

zone_york_dict = {'RMF': 'residential',
             'RR': 'residential',
             'R33': 'residential',
             'x': 'not_include',
             'NB': 'commercial_industry',
             'WCI': 'commercial_industry',
             'EO': 'commercial_industry',
             'R13': 'residential',
             'LB': 'commercial_industry',
             'R7': 'not_include',
             'GB': 'commercial_industry',
             'YVA': 'not_include',
             'IL': 'commercial_industry',
             'RC': 'not_include', # visualization includes some commercial area and green space, but after joining the building data, a lot of the areas actually covered with residential
             'PD': 'residential', # residential house planned or had already constructed
             'R20': 'residential',
             'IG': 'commercial_industry'}

# zone_dict = {'commercial_industry': ['NB', 'WCI', 'EO', 'LB', 'GB', 'IL', 'IG'],
#              'residential': ['RMF', 'RR', 'R33', 'R13', 'R20']}


york_gdf['zone_group'] = york_gdf['ZONING'].map(zone_york_dict)
york_gdf['source'] = 'york'


# processing JCC data
jcc_commercial = ['BLDG - Commercial', 'BLDG - Public Building', 'BLDG - Church']
jcc_residential = ['BLDG - Residential', 'BLDG - Mobile Home', 'BLDG - Multi-Family', 'BLDG - Timeshare', 'BLDG - Retirement Community', 'Residential']

# Define a function that checks if a category belongs to commercial or residential
def classify_zoing(value):
    if value in jcc_commercial:
        return 'commercial_industry'
    elif value in jcc_residential:
        return 'residential'
    else:
        return 'other'  # If the category doesn't match, assign 'other'

# Apply the function to create a new 'classification' column
jcc_gdf['zone_group'] = jcc_gdf['Code'].apply(classify_zoing)
jcc_gdf['source'] = 'jcc'

# jcc_gdf.drop(['created_us', 'created_da', 'last_edite', 'last_edi_1', 'County', 'FID_County', 'GIS_Notes', 'FID_LandUs', 'Detail', 'OBJECTID'], axis=1, inplace=True)
# york_gdf.drop(['CHANGE_DAT', 'GlobalID', 'OBJECTID', 'GPIN', 'MAP', 'COND', 'PROFFER'], axis=1, inplace=True)

jcc_gdf = jcc_gdf[['Code', 'zone_group', 'source', 'geometry']]
york_gdf = york_gdf[['ZONING', 'zone_group', 'source', 'geometry']]
merged_df = pd.concat([jcc_gdf, york_gdf])
filtered_df = merged_df[merged_df['zone_group'].isin(['commercial_industry', 'residential'])]


# Processing building data and merge the building data with zoning information from York and JCC
bd_gdf['poly_geo'] = bd_gdf.geometry
bd_gdf['geometry'] = bd_gdf.geometry.centroid

# join building with zoning data
bd_gdf = bd_gdf.sjoin(merged_df, how="left", predicate="within")
# keep buildings that have zoning information
subbd_gdf = bd_gdf[bd_gdf['zone_group'].isin(['commercial_industry', 'residential'])]

subbd_gdf['geometry'] = subbd_gdf['poly_geo']
subbd_gdf.drop(['poly_geo'], axis=1, inplace=True)
# subbd_gdf.to_file('../data/processed/building_tag.shp')


# Function to calculate the shortest and longest side of the polygon
def calculate_side_lengths(polygon):
    # Get the exterior coordinates of the polygon (ignoring holes for simplicity)
    exterior_coords = list(polygon.exterior.coords)

    # Initialize a list to store the lengths of each side
    side_lengths = []

    # Iterate through the coordinates to calculate the length of each side
    for i in range(len(exterior_coords) - 1):
        # Create a line segment between each consecutive pair of coordinates
        line = LineString([exterior_coords[i], exterior_coords[i + 1]])
        # Calculate the length of the line segment and add it to the list
        side_lengths.append(line.length)

    return min(side_lengths), max(side_lengths)


# Function to calculate the length and width of a polygon using its bounding box (envelope)
def calculate_length_width(polygon):
    # Get the bounding box (minimum bounding rectangle) of the polygon
    minx, miny, maxx, maxy = polygon.bounds

    # Calculate the width (difference in x direction) and length (difference in y direction)
    width = maxx - minx
    length = maxy - miny

    # Return the length and width
    return max(length, width), min(length, width)


# Function to calculate rectangular fit for a polygon
def rectangular_fit(polygon):
    # Area of the original polygon
    polygon_area = polygon.area

    # Get the minimum bounding rectangle (MBR) or envelope of the polygon
    mbr = polygon.envelope

    # Area of the MBR
    mbr_area = mbr.area

    # Rectangular fit is the ratio of the polygon's area to the MBR's area
    if mbr_area > 0:
        rect_fit = polygon_area / mbr_area
    else:
        rect_fit = 0  # To handle cases where MBR area is zero (unlikely for valid polygons)

    return rect_fit

# Calculate Compactness (Shape Index)
def compactness(polygon):
    # Area of the polygon
    polygon_area = polygon.area

    # Perimeter of the polygon
    polygon_perimeter = polygon.length

    # Compactness formula: 4 * pi * Area / (Perimeter^2)
    if polygon_perimeter > 0:
        compactness_value = (4 * np.pi * polygon_area) / (polygon_perimeter ** 2)
    else:
        compactness_value = 0  # To handle cases where perimeter is zero (unlikely for valid polygons)

    return compactness_value



"""
Generating a series of Shape/Geometry Features
"""
subbd_gdf[['side_short', 'side_long']] = subbd_gdf['geometry'].apply(lambda x: pd.Series(calculate_side_lengths(x)))
# calculate the area, height, width, and perimeter of the polygons
subbd_gdf[['bds_length', 'bds_width']] = subbd_gdf['geometry'].apply(lambda x: pd.Series(calculate_length_width(x)))
subbd_gdf['area'] = subbd_gdf['geometry'].area
subbd_gdf['perimeter'] = subbd_gdf['geometry'].length
subbd_gdf['len2wid'] = subbd_gdf.apply(lambda x: x['bds_length']/x['bds_width'], axis=1) # calculate the Length-to-Width Ratio
# Rectangular Fit: A metric to evaluate how well the building fits into a rectangle (often higher for commercial buildings).
subbd_gdf['rectangular_fit'] = subbd_gdf['geometry'].apply(rectangular_fit)
# Compactness/Shape Index: Assess how regular or compact the shape of the building is (e.g., circular, rectangular).
subbd_gdf['compactness'] = subbd_gdf['geometry'].apply(compactness)




#
# # Extract spectral information from NAIP
# 
# 
# # Load shapefile using geopandas
# shapefile = gpd.read_file(shapefile_path)
# 
# # Open the 4-band GeoTIFF using rasterio
# with rasterio.open(geotiff_path) as src:
#     # Check the number of bands (should be 4)
#     bands = src.count
# 
#     # Create an empty list to store statistics for each polygon and each band
#     all_band_stats = []
# 
#     # Loop through each band in the GeoTIFF (1 to 4)
#     for band_id in range(1, bands + 1):
#         # Read data for the current band
#         band_data = src.read(band_id)
# 
#         # Calculate zonal statistics for the current band
#         stats = zonal_stats(shapefile, band_data, affine=src.transform, stats=['min', 'max', 'mean', 'std', 'median', 'count'],
#                             nodata=src.nodata)
# 
#         # Append statistics for the current band
#         all_band_stats.append(stats)
# 
# 










