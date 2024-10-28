

import pandas as pd
import geopandas as gpd
import rasterio
import os
import numpy as np
from rasterstats import zonal_stats
from shapely.geometry import LineString
import ast
from skimage import feature
from skimage.measure import shannon_entropy
from helpers import calculate_side_lengths, calculate_length_width, rectangular_fit, compactness, calculate_texture_features
import matplotlib.pyplot as plt
from skimage.feature import greycomatrix, greycoprops
from shapely.geometry import box
from rasterio.mask import mask

working_dir = os.path.abspath('../')
naip_dir = os.path.join(working_dir, 'data/NAIP')
buildings = os.path.join(working_dir, 'data/processed/building_tag_tiff.shp')
gdf = gpd.read_file(buildings)

geom_feat = False
text_feat = False

"""
Generating a series of Shape/Geometry Features
"""
if geom_feat:
    gdf[['side_short', 'side_long']] = gdf['geometry'].apply(lambda x: pd.Series(calculate_side_lengths(x)))
    # calculate the area, height, width, and perimeter of the polygons
    gdf[['bds_length', 'bds_width']] = gdf['geometry'].apply(lambda x: pd.Series(calculate_length_width(x)))
    gdf['area'] = gdf['geometry'].area
    gdf['perimeter'] = gdf['geometry'].length
    gdf['len2wid'] = gdf.apply(lambda x: x['bds_length']/x['bds_width'], axis=1) # calculate the Length-to-Width Ratio
    # Rectangular Fit: A metric to evaluate how well the building fits into a rectangle (often higher for commercial buildings).
    gdf['rectangular_fit'] = gdf['geometry'].apply(rectangular_fit)
    # Compactness/Shape Index: Assess how regular or compact the shape of the building is (e.g., circular, rectangular).
    gdf['compactness'] = gdf['geometry'].apply(compactness)



"""
Generating texture features such as homogeneity, contrast, and entropy 
Texture Homogeneity: Uniformity in texture (commercial buildings tend to have more uniform roofing materials, whereas residential buildings may have more varied textures).
Contrast: Assess variation in pixel intensities within the object.
Entropy: Quantifies randomness in texture; can differentiate materials used in buildings.
"""

if text_feat:
    # Iterate over each unique GeoTIFF file reference
    texture_features = []

    for geotiff_file in gdf['geotiff'].unique():
        # Filter polygons for the current GeoTIFF
        subset_gdf = gdf[gdf['geotiff'] == geotiff_file]

        # Open corresponding GeoTIFF
        with rasterio.open(f"{naip_dir}/{geotiff_file}") as src:

            if subset_gdf.crs != src.crs:
                subset_gdf = subset_gdf.to_crs(src.crs)

            for idx, row in subset_gdf.iterrows():
                # Mask the GeoTIFF with the polygon
                geom = [row['geometry'].buffer(0.1)] # if polygons are lines or very narrow, mask can struggle, thus add a small buffer
                out_image, out_transform = mask(src, geom, crop=True)

                # Calculate texture features for each band
                features = {}
                for band_num in range(out_image.shape[0]):  # Loop over each band
                    homogeneity, contrast, entropy = calculate_texture_features(out_image[band_num])
                    features[f'band{band_num + 1}_homogeneity'] = homogeneity
                    features[f'band{band_num + 1}_contrast'] = contrast
                    features[f'band{band_num + 1}_entropy'] = entropy

                # Append features to texture_features list
                texture_features.append(features)

    # Add features to original GeoDataFrame
    features_df = gpd.GeoDataFrame(texture_features)
    gdf = gdf.join(features_df)

"""
Generating Spectral Features
A lower of Coefficient of Variation value indicates higher homogeneity.
"""





"""
Generating Spatial/Contextual Features 
"""



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





