
import os
from lulc_processing import create_building_geotiff, reclass_lulc

working_dir = os.path.abspath('../')
# data_path = os.path.join(working_dir, 'data/lulc/math_51115_landcover_2018.tif')
lulc_path = os.path.join(working_dir, 'data/lulc/math_51115_lu_2018_26918.tif')
lulc_reclass_path = os.path.join(working_dir, 'data/processed/Mathew/math_lu_2018_reclass.tif')

building_path = os.path.join(working_dir, 'prediction/mathew_prediction.shp')
building_rst_path = os.path.join(working_dir, 'prediction/mathew_building_rst.tif')

is_building_process = False
is_lulc_process = False


"""
structure: commercial and residential -> 1, 2, 0
"""

# Processing building data
if is_building_process:
    create_building_geotiff(lulc_path, building_path, building_rst_path)

"""
Reclassify lulc
"""

if is_lulc_process:
    reclass_lulc(lulc_path, lulc_reclass_path)

#
# is_combined = True
#
# if is_combined:





















