
import os
import joblib
import geopandas as gpd
import pickle

working_dir = os.path.abspath('../')
model_path = os.path.join(working_dir, 'models/random_forest_model.pkl')

# load processed Mathew data
data_path = os.path.join(working_dir, 'data/processed/Mathew/mathew_building_features.shp')

gdf = gpd.read_file(data_path)

# 'area', 'perimeter', 'b4_median'

# # all features from the raw data
# x_feat = ['side_short', 'side_long', 'bds_length', 'bds_width', 'len2wid', 'geo_rect_f', 'geo_compac', 'area', 'perimeter',
#             'b1_tt_homo', 'b1_tt_cont', 'b1_tt_etrp', 'b2_tt_homo', 'b2_tt_cont','b2_tt_etrp',
#             'b3_tt_homo', 'b3_tt_cont', 'b3_tt_etrp', 'b4_tt_homo', 'b4_tt_cont', 'b4_tt_etrp',
#             'b1_mean', 'b1_std', 'b1_cv', 'b1_spc_hom', 'b2_mean', 'b2_std', 'b2_cv', 'b2_spc_hom',
#             'b3_mean', 'b3_std', 'b3_cv', 'b3_spc_hom', 'b4_mean',
#             'b4_std', 'b4_cv', 'b4_spc_hom']


# Load the model from the file
loaded_model, top_features = joblib.load(model_path)
filtered_gdf = gdf[top_features]

# fill the missing rows with the mean value
filtered_gdf = filtered_gdf.fillna(filtered_gdf.mean())

# Load and preprocess the data
X = filtered_gdf[top_features]

# Prediction
predictions = loaded_model.predict(X)
gdf['predict'] = predictions
gdf.to_file(os.path.join(working_dir, 'prediction/mathew_prediction.shp'))
