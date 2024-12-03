

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
import argparse

# working_dir = os.path.abspath('../')
# buildings = os.path.join(working_dir, 'data/processed/Mathew/building_mathew_tiff.shp')
# naip_dir = os.path.join(working_dir, 'data/NAIP/Mathew')
# output_path = os.path.join(working_dir, 'data/processed/Mathew/mathew_building_features.shp')
# gdf = gpd.read_file(buildings)
#
# geom_feat = True
# text_feat = True
# spec_feat = True

def main():

    parser = argparse.ArgumentParser(description='Description of your script.')
    parser.add_argument('input_file', type=str, help='Path to the input shapefile file.')
    parser.add_argument('geotiff_dir', type=str, help='Path to the folder of NAIP images.')
    parser.add_argument('geom_feat', type=str, help='Whether to generate geom features. default=False', default=False)
    parser.add_argument('text_feat', type=str, help='Whether to generate texture features. default=False', default=False)
    parser.add_argument('spec_feat', type=str, help='Whether to generate spectral features. default=False', default=False)
    parser.add_argument('--output_file', type=str, help='Path to the output file.', default='output.shp')
    args = parser.parse_args()

    gdf = gpd.read_file(args.input_file)

    """
    Generating a series of Shape/Geometry Features
    """
    if args.geom_feat:
        gdf[['side_short', 'side_long']] = gdf['geometry'].apply(lambda x: pd.Series(calculate_side_lengths(x)))
        # calculate the area, height, width, and perimeter of the polygons
        gdf[['bds_length', 'bds_width']] = gdf['geometry'].apply(lambda x: pd.Series(calculate_length_width(x)))
        gdf['area'] = gdf['geometry'].area
        gdf['perimeter'] = gdf['geometry'].length
        gdf['len2wid'] = gdf.apply(lambda x: x['bds_length']/x['bds_width'], axis=1) # calculate the Length-to-Width Ratio
        # Rectangular Fit: A metric to evaluate how well the building fits into a rectangle (often higher for commercial buildings).
        gdf['geo_rect_f'] = gdf['geometry'].apply(rectangular_fit)
        # Compactness/Shape Index: Assess how regular or compact the shape of the building is (e.g., circular, rectangular).
        gdf['geo_compac'] = gdf['geometry'].apply(compactness)



    """
    Generating texture features such as homogeneity, contrast, and entropy 
    Texture Homogeneity: Uniformity in texture (commercial buildings tend to have more uniform roofing materials, whereas residential buildings may have more varied textures).
    Contrast: Assess variation in pixel intensities within the object.
    Entropy: Quantifies randomness in texture; can differentiate materials used in buildings.
    """

    if args.text_feat:
        # Iterate over each unique GeoTIFF file reference
        texture_features = []
        spectral_features = []

        for geotiff_file in gdf['geotiff'].unique():
            # Filter polygons for the current GeoTIFF
            subset_gdf = gdf[gdf['geotiff'] == geotiff_file]

            # Open corresponding GeoTIFF
            with rasterio.open(f"{args.geotiff_dir}/{geotiff_file}") as src:

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
                        features[f'b{band_num + 1}_tt_homo'] = homogeneity # the maximum length of name is 10
                        features[f'b{band_num + 1}_tt_cont'] = contrast
                        features[f'b{band_num + 1}_tt_etrp'] = entropy

                    # Append features to texture_features list
                    texture_features.append(features)

        # Add features to original GeoDataFrame
        features_df = gpd.GeoDataFrame(texture_features)
        gdf = gdf.join(features_df)

    """
    Generating Spectral Features
    A lower of Coefficient of Variation value indicates higher homogeneity.
    """
    if spec_feat:
        # Iterate over each unique GeoTIFF file reference
        spectral_features = []

        for geotiff_file in gdf['geotiff'].unique():
            # Filter polygons for the current GeoTIFF
            subset_gdf = gdf[gdf['geotiff'] == geotiff_file]
            # Create an empty list to store statistics for each subset_gdf
            all_band_stats = []
            # Open corresponding GeoTIFF
            with rasterio.open(f"{args.geotiff_dir}/{geotiff_file}") as src:
                bands = src.count

                # Loop through each band in the GeoTIFF (1 to 4)
                for band_id in range(1, bands + 1):
                    # Read data for the current band
                    band_data = src.read(band_id)

                    # Calculate zonal statistics for the current band
                    stats = zonal_stats(subset_gdf, band_data, affine=src.transform,
                                        stats=['mean', 'std', 'median'],
                                        nodata=src.nodata)

                    stats_df = gpd.GeoDataFrame(stats)
                    stats_df['cv'] = stats_df['std'] / stats_df['mean']
                    stats_df['spc_homo'] = stats_df['cv'].apply(lambda x: 1/1+x) # 1 / 1 + 'cv'
                    stats_df = stats_df.rename(columns={"mean": f'b{band_id}_mean', "std": f'b{band_id}_std', "median": f'b{band_id}_median', "cv": f'b{band_id}_cv', "spc_homo": f'b{band_id}_spc_homo'})
                    all_band_stats.append(stats_df)

            sta_all_df = pd.concat(all_band_stats, axis=1) # for each subset_gdf get the all band statistics with the corresponding name changed
            # reset the index of subset_df and sta_all_df, so they can merge on the axis=1, with correct dimensions
            sta_all_df = sta_all_df.reset_index(drop=True)
            subset_gdf = subset_gdf.reset_index(drop=True)

            subset_gdf = pd.concat([subset_gdf, sta_all_df], axis=1) # combine the all band statistics with the subset_gdf
            spectral_features.append(subset_gdf) # all columns variables are included

        gdf = pd.concat(spectral_features, ignore_index=True) # concatenate rows

    gdf.to_file(output_path)


if __name__ == "__main__":
    main()