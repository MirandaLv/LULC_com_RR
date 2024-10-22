
# processing zoning data and lulc data to extract the land with label

import pandas as pd
import geopandas as gpd
import rasterio
import os
import numpy as np


working_dir = os.path.abspath('../')

york_zone = os.path.join(working_dir, 'data/Zoning_York/zoing_york_26918.shp')
jcc_lulc = os.path.join(working_dir, 'data/JCC_Land_Use/jcc_lu_26918.shp')
buildings = os.path.join(working_dir, 'data/buildingfootprint/building_footprint_proj.shp')

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
             'RC': 'commercial_industry', # visualization includes some commercial area and green space
             'PD': 'residential', # residential house planned or had already constructed
             'R20': 'residential',
             'IG': 'commercial_industry'}

# zone_dict = {'commercial_industry': ['NB', 'WCI', 'EO', 'LB', 'GB', 'IL', 'IG'],
#              'residential': ['RMF', 'RR', 'R33', 'R13', 'R20']}


york_gdf['zone_group'] = york_gdf['ZONING'].map(zone_york_dict)
york_gdf['source'] = 'york'
valid_york_gdf = york_gdf[york_gdf['zone_group'].isin(['commercial', 'residential'])]


# processing JCC data
jcc_commercial = ['BLDG - Commercial', 'BLDG - Public Building', 'BLDG - Church']
jcc_residential = ['BLDG - Residential', 'BLDG - Mobile Home', 'BLDG - Multi-Family', 'BLDG - Timeshare', 'BLDG - Retirement Community', 'Residential']

# Define a function that checks if a category belongs to commercial or residential
def classify_zoing(value):
    if value in jcc_commercial:
        return 'commercial'
    elif value in jcc_residential:
        return 'residential'
    else:
        return 'other'  # If the category doesn't match, assign 'other'

# Apply the function to create a new 'classification' column
jcc_gdf['zone_group'] = jcc_gdf['Code'].apply(classify_zoing)
jcc_gdf['source'] = 'jcc'
valid_jcc_gdf = jcc_gdf[jcc_gdf['zone_group'].isin(['commercial', 'residential'])]

jcc_gdf.drop(['created_us', 'created_da', 'last_edite', 'last_edi_1', 'County', 'FID_County', 'GIS_Notes', 'FID_LandUs', 'Detail', 'OBJECTID'], axis=1, inplace=True)
york_gdf.drop(['CHANGE_DAT', 'GlobalID', 'OBJECTID', 'GPIN', 'MAP', 'COND', 'PROFFER'], axis=1, inplace=True)

# merged_df = pd.concat([jcc_gdf, york_gdf])
# filtered_df = merged_df[merged_df['zone_group'].isin(['commercial', 'residential'])]






