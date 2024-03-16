import cv2
import os
import glob
import numpy as np
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import shutil

# Function to extract color histogram features
def extract_features(image_path, bins=(8, 8, 8)):
    image = cv2.imread(image_path)
    hist = cv2.calcHist([image], [0, 1, 2], None, bins, [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()

# Function to load all images from a directory and its subdirectories
def load_images_from_folder(folder):
    images = []
    for filename in glob.glob(os.path.join(folder, '**', '*.jpg'), recursive=True):
        images.append(filename)
    return images

# Load images
folder_path = 'F:/Project492/test_images'
image_paths = load_images_from_folder(folder_path)

features = []
for path in image_paths:
    feature = extract_features(path)
    features.append(feature)

# Determine the optimal number of clusters
inertias = []
K = range(2, 5)  # replace 5 with the maximum number of clusters you want to consider

for k in K:
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(features)
    inertias.append(kmeans.inertia_)

# Plot the elbow
plt.figure(figsize=(8, 4))
plt.plot(K, inertias, 'bo-')
plt.xlabel('Number of clusters')
plt.ylabel('Inertia')
plt.show()

# Choose the number of clusters where inertia starts to decrease more slowly
optimal_k = inertias.index(min(inertias)) + 2  # +2 because K starts from 2

# Cluster images using K-means with the optimal number of clusters
kmeans = KMeans(n_clusters=optimal_k)
kmeans.fit(features)

# Create a directory for each cluster
for i in range(optimal_k):
    os.makedirs(f'output/cluster_{i}', exist_ok=True)

# Move each image to its cluster directory
for path, label in zip(image_paths, kmeans.labels_):
    shutil.move(path, f'output/cluster_{label}/{os.path.basename(path)}')