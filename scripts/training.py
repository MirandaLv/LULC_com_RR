
import pandas as pd
import geopandas as gpd
import os
from matplotlib import pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE # over sampling/simulation the minority class
from imblearn.under_sampling import RandomUnderSampler # under sampling the majority class
import joblib

working_dir = os.path.abspath('../')
data = os.path.join(working_dir, 'data/processed/building_features.shp')

gdf = gpd.read_file(data)

# 'area', 'perimeter', 'b4_median'

# select features for model prediction
y_feat = 'zone_group'
x_feat = ['side_short', 'side_long', 'bds_length', 'bds_width', 'len2wid', 'geo_rect_f', 'geo_compac', 'area', 'perimeter',
            'b1_tt_homo', 'b1_tt_cont', 'b1_tt_etrp', 'b2_tt_homo', 'b2_tt_cont','b2_tt_etrp',
            'b3_tt_homo', 'b3_tt_cont', 'b3_tt_etrp', 'b4_tt_homo', 'b4_tt_cont', 'b4_tt_etrp',
            'b1_mean', 'b1_std', 'b1_cv', 'b1_spc_hom', 'b2_mean', 'b2_std', 'b2_cv', 'b2_spc_hom',
            'b3_mean', 'b3_std', 'b3_cv', 'b3_spc_hom', 'b4_mean',
            'b4_std', 'b4_cv', 'b4_spc_hom']

# Load and preprocess the data
y = gdf[y_feat]
X = gdf[x_feat]

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

print('Check on the training size for each category!')
print(y_train[y_train=='residential'].shape)
print(y_train[y_train=='commercial_industry'].shape)

########
# Model with no additional processing of data imbalance
########
# Set up the Random Forest model
# Using class_weight='balanced' to handle class imbalance
rf_model = RandomForestClassifier(class_weight='balanced', random_state=42, n_estimators=100)

# Train the model
rf_model.fit(X_train, y_train)

# Make predictions and evaluate the model
y_pred = rf_model.predict(X_test)

# Print evaluation metrics
print("Classification Report:\n", classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Feature importance analysis
importances = rf_model.feature_importances_
feature_names = X.columns
feature_importance_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
feature_importance_df = feature_importance_df.sort_values(by='importance', ascending=False)
print("Feature Importances:\n", feature_importance_df)


# Top features
threshold = 0.02
top_features = feature_importance_df[feature_importance_df['importance'] >= threshold]["feature"].tolist()

X_train_selected = X_train[top_features]
X_test_selected = X_test[top_features]

# Train a new Random Forest model using selected features
rf_new = RandomForestClassifier(class_weight='balanced', random_state=42, n_estimators=100)
rf_new.fit(X_train_selected, y_train)

# Make predictions and evaluate the model
y_pred_rfnew = rf_new.predict(X_test_selected)

# Print evaluation metrics
print("Classification Report:\n", classification_report(y_test, y_pred_rfnew))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_rfnew))



########
# Model with data balanced using SMOTE to over sample under-represented case
########


# Dealing with imbalance issue with SMOTE
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_selected, y_train)

print('Check on the training size for each category after resampling!')
print(y_train_resampled[y_train_resampled=='residential'].shape)
print(y_train_resampled[y_train_resampled=='commercial_industry'].shape)

# Train Random Forest Classifier
clf_over_spl = RandomForestClassifier(random_state=42)
clf_over_spl.fit(X_train_resampled, y_train_resampled)

# Evaluate model
y_pred_balanced = clf_over_spl.predict(X_test_selected)

print("Classification Report:\n", classification_report(y_test, y_pred_balanced))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_balanced))


# # Feature importance analysis
# importances = clf_over_spl.feature_importances_
# feature_names = X.columns
# feature_importance_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
# feature_importance_df = feature_importance_df.sort_values(by='importance', ascending=False)
# print("Feature Importances:\n", feature_importance_df)



########
# Model with data balanced using undersampling the majority category
########


# Dealing with imbalance issue with undersampling the majority
rus = RandomUnderSampler()
X_res, y_res = rus.fit_resample(X_train_selected, y_train)

print('Check on the training size for each category after resampling!')
print(y_res[y_res=='residential'].shape)
print(y_res[y_res=='commercial_industry'].shape)

# Train Random Forest Classifier
clf_ud_spl = RandomForestClassifier(random_state=42)
clf_ud_spl.fit(X_res, y_res)

# Evaluate model
y_pred_res = clf_ud_spl.predict(X_test_selected)

print("Classification Report:\n", classification_report(y_test, y_pred_res))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_res))

#
# # Feature importance analysis
# importances = clf_ud_spl.feature_importances_
# feature_names = X.columns
# feature_importance_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
# feature_importance_df = feature_importance_df.sort_values(by='importance', ascending=False)
# print("Feature Importances:\n", feature_importance_df)


# # Save the model without over or under sampling strategies
joblib.dump(rf_model, os.path.join(working_dir, 'models/random_forest_model.pkl'))
# joblib.dump(clf_over_spl, os.path.join(working_dir, 'models/RF_overSampling.pkl'))
# joblib.dump(clf_ud_spl, os.path.join(working_dir, 'models/RF_underSampling.pkl'))