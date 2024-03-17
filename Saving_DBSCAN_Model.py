from sklearn.cluster import DBSCAN
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing import image
from keras.models import Model
import numpy as np
import os
import tensorflow as tf
import shutil


# Load VGG16 model
base_model = VGG16(weights='imagenet')
model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

# Save the model
model.save('vgg16_model.keras')
