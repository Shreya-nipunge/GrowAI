import pickle
import numpy as np
import cv2
from tensorflow import keras
import os


disease_model = keras.models.load_model(r'D:\Codes\Krishimitra\GrowAI\ai\cv\models\plant_disease_model.h5')

with open(r'D:\Codes\Krishimitra\GrowAI\ai\cv\models\plant_disease_labels.pkl', "rb") as f:
    disease_labels = pickle.load(f)

def preprocess_image(image_path, target_size=(224, 224)):
    """
    Preprocess an image for model input.
    """
    img = cv2.imread(image_path)
    img = cv2.resize(img, target_size)
    img = img / 255.0  # normalize
    img = np.expand_dims(img, axis=0)
    return img

def predict_disease(image_path):
    """
    Predict plant disease from an image.
    """
    try:
        img = preprocess_image(image_path)
        prediction = disease_model.predict(img)
        predicted_class = np.argmax(prediction, axis=1)[0]
        return disease_labels[predicted_class]
    except Exception as e:
        return f"Error in prediction: {str(e)}"

# Example usage
if __name__ == "__main__":
    result = predict_disease("sample_leaf.jpg")
    print("Predicted disease:", result)
