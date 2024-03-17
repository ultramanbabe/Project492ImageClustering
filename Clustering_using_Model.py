from keras.models import load_model
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image
from sklearn.cluster import DBSCAN
import numpy as np
import os
import shutil

# Directory containing images
dir_path = 'F:/Project492/test_images/'

# Output directory for clustered images
output_dir = 'F:/Project492/static/clustered_images'

# Load the saved model
model = load_model('vgg16_model.keras')

def extract_features(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_data = image.img_to_array(img)
        img_data = np.expand_dims(img_data, axis=0)
        img_data = preprocess_input(img_data)
        features = model.predict(img_data)
        return features.flatten()
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        return None

# Extract features for all images
all_features = []
image_paths = []
for img_path in os.listdir(dir_path):
    full_img_path = os.path.join(dir_path, img_path)
    features = extract_features(full_img_path)
    if features is not None:
        all_features.append(features)
        image_paths.append(full_img_path)

# Use DBSCAN to cluster features
dbscan = DBSCAN(eps=130, min_samples=2)
clusters = dbscan.fit_predict(np.array(all_features))

# Copy images to output directory
for img_path, cluster in zip(image_paths, clusters):
    print(f'{img_path} is in cluster {cluster}')
    # Create a directory for the cluster if it doesn't exist
    cluster_dir = os.path.join(output_dir, str(cluster))
    os.makedirs(cluster_dir, exist_ok=True)
    # Copy the image to the cluster directory
    shutil.copy(img_path, cluster_dir)