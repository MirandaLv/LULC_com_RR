
import os
import geopandas as gpd
from lulc_processing import create_building_geotiff, reclass_lulc, combine_data
import argparse

"""
Code processing to convert the structure inventory published by: https://www.nature.com/articles/s41597-024-03219-x#Tab2
into two major categories: commercial_industry, and residential
"""

# working_dir = os.path.abspath('../')
# structure_path = os.path.join(working_dir, "data/structure_inventory/Mathew_VA_structures_26918.shp")
# structure_reclass_path = os.path.join(working_dir, "data/structure_inventory/Mathew_VA_structures_reclass.shp")
# lulc_path = os.path.join(working_dir, "data/lulc/math_51115_lu_2018_26918.tif")
# building_rst_path = os.path.join(working_dir, 'data/structure_inventory/mathew_structure_rst.tif')

def main():

    parser = argparse.ArgumentParser(description='Description of your script.')
    parser.add_argument("-b", "--building_file", type=str, help="Path to the building shapefile.")
    parser.add_argument("-lulc", "--lulc_file", type=str, help="Path to the lulc file.")
    # Outputs
    parser.add_argument("-olr", "--lulc_reclass", type=str, help="Path to the lulc reclassed file.", default='lulc_reclasss.tif')
    parser.add_argument("-obr", "--building_reclass", type=str, help="Path to the building reclassed shapefile.", default='structure_reclasss.shp')
    parser.add_argument("-o", '--output_file', type=str, help='Path to the output file.', default='output.shp')

    args = parser.parse_args()

    print("Structure reclassification.....")
    # Shapefile processing to reclassify the building categories
    gdf = gpd.read_file(args.building_file)
    # all_classes = gdf.OCC_CLS.unique().tolist()
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
    # Add a buffer of 2 meters
    gdf['geometry'] = gdf.geometry.buffer(2)

    # Rasterization of building category file
    print("Structure geotiff reclassification.....")
    create_building_geotiff(args.lulc_file, gdf, args.building_reclass, "zone_group")
    # Reclass lulc
    print("LULC reclassification.....")
    reclass_lulc(args.lulc_file, args.lulc_reclass)
    # Combine lulc with rst structure
    print("Data combination.....")
    combine_data(args.lulc_reclass, args.building_reclass, args.output_file)

if __name__ == "__main__":
    main()



