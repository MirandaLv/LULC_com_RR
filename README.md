# LULC_com_RR

Building footprints will be classified as either commercial or residential to help identify developed areas within the NLDC that correspond to residential or commercial land use.

### Data source:
- Zoning shapefile from York county, which include a zoning map with its corresponding zoning information.
- JCC_land_use: a shapefile with land use information of James county. 

###Scripts description

- data_processing.py: categorize the zoning/lulc information into commercial and residential, merge with building footprint data;
- geotiff_processing.py: combine the building footprint with the corresponding NAIP image;
- feature_gen.py: feature generation for geometry (area, perimeter, ratio length/width), texture (texture homogeneity, contrast, and entropy), spectral (spectral homogeneity, mean, std,  cefficient of variation, etc);
- training.py: model building, training, validation;
- helper.py: functions to calculate different features;