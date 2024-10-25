
import pandas as pd
import geopandas as gpd
import os

working_dir = os.path.abspath('../')
data = os.path.join(working_dir, 'data/processed/building_tag.shp')

gdf = gpd.read_file(data)

print(gdf.columns)
