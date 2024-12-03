
import os
from lulc_processing import create_building_geotiff, reclass_lulc, combine_lulc_building, combine_data
import argparse


working_dir = os.path.abspath('../')
# data_path = os.path.join(working_dir, 'data/lulc/math_51115_landcover_2018.tif')
lulc_path = os.path.join(working_dir, 'data/lulc/math_51115_lu_2018_26918.tif')
lulc_reclass_path = os.path.join(working_dir, 'data/processed/Mathew/math_lu_2018_reclass.tif')

building_path = os.path.join(working_dir, 'prediction/mathew_prediction.shp')
# building_rst_path = os.path.join(working_dir, 'prediction/mathew_building_rst.tif')
building_rst_path = os.path.join(working_dir, 'data/structure_inventory/mathew_structure_rst.tif')

is_building_process = False
is_lulc_process = False


def main():

    parser = argparse.ArgumentParser(description='Description of your script.')
    parser.add_argument("-lulc", "--lulc_file", type=str, help="Path to the lulc file.")
    parser.add_argument("-lulc_r", "--lulc_reclass", type=str, help="Path to the lulc reclassed file.")
    parser.add_argument("-b", "--building_file", type=str, help="Path to the building shapefile.")
    parser.add_argument("-br", "--building_reclass", type=str, help="Path to the building reclassed tiff file.")
    parser.add_argument("-s", "--spec_feat", help="Whether to generate spectral features. default=False",
                        action="store_true")
    parser.add_argument("-o", '--output_file', type=str, help='Path to the output file.', default='output.shp')
    args = parser.parse_args()

"""
structure: commercial and residential -> 1, 2, 0
"""

# Processing building data [from prediction]
if is_building_process:
    create_building_geotiff(lulc_path, building_path, building_rst_path)

"""
Reclassify lulc
"""

if is_lulc_process:
    reclass_lulc(lulc_path, lulc_reclass_path)


is_combined = True

out_path = os.path.join(working_dir, 'prediction/lulc_structure_merge.tif')

if is_combined:
    combine_data(lulc_reclass_path, building_rst_path, out_path)

























