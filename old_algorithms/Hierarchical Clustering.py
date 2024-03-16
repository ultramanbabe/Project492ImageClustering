from sklearn.preprocessing import StandardScaler
import os
import cv2
from scipy.cluster.hierarchy import fcluster, linkage
from matplotlib import pyplot as plt
import shutil

# Directory containing images
img_dir = 'F:/Project492/Images_test/15-02-2024/'
# Define the output directory
output_dir = 'F:/Project492/output_images/'

# Load images
images = []
image_paths = []

# Recursive function to process all images in directory and subdirectories
def process_images(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img = cv2.imread(os.path.join(directory, filename), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                images.append(img.flatten())
                image_paths.append(os.path.join(directory, filename))
        else:
            if os.path.isdir(os.path.join(directory, filename)):
                process_images(os.path.join(directory, filename))

# Call the function on the root directory
process_images(img_dir)

# Standardize features
scaler = StandardScaler()
images = scaler.fit_transform(images)

# Generate the linkage matrix
Z = linkage(images, 'ward')

# Determine the clusters at distance 5500 (t)
max_d = 5500
clusters = fcluster(Z, t=max_d, criterion='distance')

# Create a dendrogram
#dendrogram(Z)

# Display the dendogram
#plt.title('Hierarchical Clustering Dendrogram')
#plt.xlabel('Image index')
#plt.ylabel('Distance')
#plt.show()

# Move images to cluster folders
for i in range(len(clusters)):
    # Create a new directory for the cluster in the output directory
    cluster_dir = os.path.join(output_dir, 'cluster_' + str(clusters[i]))
    if not os.path.exists(cluster_dir):
        os.makedirs(cluster_dir)
    # Move the image to the new directory
    shutil.move(image_paths[i], os.path.join(cluster_dir, os.path.basename(image_paths[i])))