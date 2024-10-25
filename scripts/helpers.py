
import numpy as np
from shapely.geometry import LineString
import rasterio
import numpy as np
from rasterio.mask import mask
from skimage.feature import greycomatrix, greycoprops
from skimage.measure import shannon_entropy


# Function to calculate the shortest and longest side of the polygon
def calculate_side_lengths(polygon):
    # Get the exterior coordinates of the polygon (ignoring holes for simplicity)
    exterior_coords = list(polygon.exterior.coords)

    # Initialize a list to store the lengths of each side
    side_lengths = []

    # Iterate through the coordinates to calculate the length of each side
    for i in range(len(exterior_coords) - 1):
        # Create a line segment between each consecutive pair of coordinates
        line = LineString([exterior_coords[i], exterior_coords[i + 1]])
        # Calculate the length of the line segment and add it to the list
        side_lengths.append(line.length)

    return min(side_lengths), max(side_lengths)


# Function to calculate the length and width of a polygon using its bounding box (envelope)
def calculate_length_width(polygon):
    # Get the bounding box (minimum bounding rectangle) of the polygon
    minx, miny, maxx, maxy = polygon.bounds

    # Calculate the width (difference in x direction) and length (difference in y direction)
    width = maxx - minx
    length = maxy - miny

    # Return the length and width
    return max(length, width), min(length, width)


# Function to calculate rectangular fit for a polygon
def rectangular_fit(polygon):
    # Area of the original polygon
    polygon_area = polygon.area

    # Get the minimum bounding rectangle (MBR) or envelope of the polygon
    mbr = polygon.envelope

    # Area of the MBR
    mbr_area = mbr.area

    # Rectangular fit is the ratio of the polygon's area to the MBR's area
    if mbr_area > 0:
        rect_fit = polygon_area / mbr_area
    else:
        rect_fit = 0  # To handle cases where MBR area is zero (unlikely for valid polygons)

    return rect_fit

# Calculate Compactness (Shape Index)
def compactness(polygon):
    # Area of the polygon
    polygon_area = polygon.area

    # Perimeter of the polygon
    polygon_perimeter = polygon.length

    # Compactness formula: 4 * pi * Area / (Perimeter^2)
    if polygon_perimeter > 0:
        compactness_value = (4 * np.pi * polygon_area) / (polygon_perimeter ** 2)
    else:
        compactness_value = 0  # To handle cases where perimeter is zero (unlikely for valid polygons)

    return compactness_value


# Function to read raster data and extract the region based on polygon
def extract_raster_values(geotiff_path, polygon):
    with rasterio.open(geotiff_path) as src:
        out_image, out_transform = mask(src, [polygon], crop=True)
        return out_image


# Function to calculate the texture features (homogeneity, contrast, entropy)
def calculate_texture_features(image_band):
    image_band = np.squeeze(image_band)

    # Ensure pixel values are integer for greycomatrix
    image_band = np.round(image_band).astype(int)

    # Compute the GLCM (Gray-Level Co-occurrence Matrix)
    glcm = greycomatrix(image_band, [1], [0], symmetric=True, normed=True)

    # Calculate Homogeneity and Contrast from the GLCM
    homogeneity = greycoprops(glcm, 'homogeneity')[0, 0]
    contrast = greycoprops(glcm, 'contrast')[0, 0]

    # Calculate Entropy
    entropy_value = shannon_entropy(image_band)

    return homogeneity, contrast, entropy_value


# Function to calculate spectral homogeneity (example: mean of pixel values as a placeholder)
def calculate_spectral_homogeneity(image_bands):
    # Here, we'll assume spectral homogeneity as the standard deviation of the band values across the region
    spectral_homogeneity = np.std(image_bands, axis=(1, 2)).mean()
    return spectral_homogeneity


# Main function to iterate over polygons and calculate features
def process_polygons_and_calculate_features(geotiff_path, polygon, band_index=0):

    # Extract pixel values for the polygon from the geotiff
    image_bands = extract_raster_values(geotiff_path, polygon)

    # Calculate texture features from the selected band (band_index)
    homogeneity, contrast, entropy_value = calculate_texture_features(image_bands[band_index])

    # # Calculate spectral homogeneity
    # spectral_homogeneity = calculate_spectral_homogeneity(image_bands)
    return homogeneity, contrast, entropy_value


