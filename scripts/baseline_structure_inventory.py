
import os
import geopandas as gpd
from lulc_processing import create_building_geotiff

"""
Code processing to convert the structure inventory published by: https://www.nature.com/articles/s41597-024-03219-x#Tab2
into two major categories: commercial_industry, and residential
"""

working_dir = os.path.abspath('../')
structure_path = os.path.join(working_dir, "data/structure_inventory/Mathew_VA_structures_26918.shp")
structure_reclass_path = os.path.join(working_dir, "data/structure_inventory/Mathew_VA_structures_reclass.shp")
lulc_path = os.path.join(working_dir, "data/lulc/math_51115_lu_2018_26918.tif")
building_rst_path = os.path.join(working_dir, 'data/structure_inventory/mathew_structure_rst.tif')


is_reclass_structure = False

if is_reclass_structure:
    gdf = gpd.read_file(structure_path)
    all_classes = gdf.OCC_CLS.unique().tolist()
    class_mapping = {"Unclassified": "commercial_industry",
                     "Residential": "residential",
                     "Commercial": "commercial_industry",
                     "Agriculture": "residential",
                    "Government": "commercial_industry",
                    "Education": "commercial_industry",
                    "Industrial": "commercial_industry",
                     "Assembly": "commercial_industry",
                     "Utility and Misc": "commercial_industry"}

    gdf['zone_group'] = gdf.OCC_CLS.map(class_mapping)
    gdf.to_file(structure_reclass_path)

create_building_geotiff(lulc_path, structure_reclass_path, building_rst_path, "zone_group")

