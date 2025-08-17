# train_plant_disease_model.py
import tensorflow as tf
import numpy as np
import pickle
import os

# Dataset directory (each subfolder = disease class)
data_dir = r"D:\Codes\Krishimitra\GrowAI\project_root\datasets\PlantVillage"

# Image preprocessing
datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1.0/255, validation_split=0.2
)

train_gen = datagen.flow_from_directory(
    data_dir, target_size=(128, 128), batch_size=16,   # reduced size & batch for less memory
    subset="training", class_mode="categorical"
)
val_gen = datagen.flow_from_directory(
    data_dir, target_size=(128, 128), batch_size=16,
    subset="validation", class_mode="categorical"
)

# Build CNN model
model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(128,128,3)),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(train_gen.num_classes, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Train model
model.fit(train_gen, validation_data=val_gen, epochs=5)  # fewer epochs for testing

# Save model safely in Keras format
model.save(r"D:\Codes\Krishimitra\GrowAI\ai\cv\models\plant_disease_model.h5")

# Save label mapping
with open(r"D:\Codes\Krishimitra\GrowAI\ai\cv\models\plant_disease_labels.pkl", "wb") as f:
    pickle.dump(list(train_gen.class_indices.keys()), f)

print("✅ Plant Disease model trained & saved.")
