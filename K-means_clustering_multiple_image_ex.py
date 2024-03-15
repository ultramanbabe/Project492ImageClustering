import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from PIL import Image

# Directory containing images
image_dir = 'F:/Project492/Images/17-02-2024/'

# Base directory to save output images
output_base_dir = 'F:/Project492/Output/'

# Get the name of the input folder
input_folder_name = os.path.basename(os.path.normpath(image_dir))

# Create the output directory with the same name as the input folder
output_dir = os.path.join(output_base_dir, input_folder_name)

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Get a list of all image files in the directory
image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]

# Dictionary to store clustering results
clusters = {}

for image_file in image_files:
    # Load the image
    image = Image.open(os.path.join(image_dir, image_file))

    # Convert the image to a numpy array
    image_array = np.array(image)

    # Flatten the image array
    image_flat = image_array.reshape(-1, 3)

    # Perform dimensionality reduction using PCA
    pca = PCA(n_components=3)
    image_flat_pca = pca.fit_transform(image_flat)

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=5, random_state=0)
    kmeans.fit(image_flat_pca)

    # Get the labels assigned to each pixel
    labels = kmeans.labels_

    # Reshape the labels array to match the original image shape
    labels_reshaped = labels.reshape(image_array.shape[:2])

    # Store the labels in the clusters dictionary
    clusters[image_file] = labels_reshaped

    # Visualize the clustered image
    plt.imshow(labels_reshaped)
    plt.axis('off')

    # Save the figure to the output directory
    output_file = os.path.join(output_dir, f'clustered_{image_file}')
    plt.savefig(output_file)

    # Clear the current figure to free memory
    plt.clf()