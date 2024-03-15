import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from PIL import Image

# Load the image
image = Image.open('F:/Project492/Images/20-02-2024/20-02-2024-1445.jpg')

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

# Visualize the clustered image
plt.imshow(labels_reshaped)
plt.axis('off')
plt.show(block=True)
#plt.savefig('F:/Project492/Images/output.jpg')
