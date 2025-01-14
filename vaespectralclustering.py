# -*- coding: utf-8 -*-
"""VAESpectralClustering.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MqjdZmmaVOarISY4_NM9COp_IhcKD3qi
"""

!pip install scikit-learn

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from keras.layers import Input, Dense, Lambda
from keras.models import Model
import keras.backend as K
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.cluster import SpectralClustering
from sklearn.kernel_approximation import Nystroem

from google.colab import drive
drive.mount('/content/drive')

# Load patient data
# Set the maximum number of columns to display
pd.set_option('display.max_columns', None)

patient_data = pd.read_csv('/content/drive/My Drive/healthcare_dataset.csv')

patient_data = patient_data.dropna()  # Handle missing values

# Format data
patient_data['Age'] = patient_data['Age'].astype(int)

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
# Iterate over each column in the DataFrame
for column in patient_data:
    # Check if the column is of object type
    if patient_data[column].dtype == 'object':
        # Fit the LabelEncoder to the column data
        patient_data[column] = le.fit_transform(patient_data[column])

scaler = StandardScaler()
scaled_data = scaler.fit_transform(patient_data)

# Define VAE model
input_dim = scaled_data.shape[1]
latent_dim = 10  # Latent space dimensionality

inputs = Input(shape=(input_dim,))
x = Dense(64, activation='relu')(inputs)
z_mean = Dense(latent_dim)(x)
z_log_var = Dense(latent_dim)(x)

def sampling(args):
    z_mean, z_log_var = args
    epsilon = K.random_normal(shape=(K.shape(z_mean)[0], latent_dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon

z = Lambda(sampling, output_shape=(latent_dim,))([z_mean, z_log_var])

decoder = Dense(64, activation='relu')(z)
outputs = Dense(input_dim, activation='linear')(decoder)

vae = Model(inputs, outputs)
vae.compile(optimizer='adam', loss='mse')

# Train VAE model
vae.fit(scaled_data, scaled_data, epochs=5, batch_size=32)

# Obtain latent representations
encoder = Model(inputs, z_mean)
latent_representations = encoder.predict(scaled_data)

# Nyström approximation
nystroem = Nystroem(kernel='rbf', n_components=100)  # Adjust n_components based on desired accuracy
similarity_matrix = nystroem.fit_transform(latent_representations)
similarity_matrix = similarity_matrix[:100, :100]
# Apply spectral clustering
n_clusters = 5  # Specify the desired number of clusters
spectral_clustering = SpectralClustering(n_clusters=n_clusters, affinity='precomputed')
patient_clusters = spectral_clustering.fit_predict(similarity_matrix)
print(f"Size of patient_clusters: {patient_clusters.shape}")

#patient_labels = spectral_clustering.labels_

import matplotlib.pyplot as plt

# Assuming latent_representations and patient_clusters are available
plt.figure(figsize=(8, 6))
plt.scatter(similarity_matrix[:, 0], similarity_matrix[:, 1], c=patient_clusters, cmap='viridis')
plt.title('Patient Clusters')
plt.xlabel('Latent Dimension 1')
plt.ylabel('Latent Dimension 2')
plt.colorbar(label='Cluster')
plt.show()