import pickle
import numpy as np
import os

# Load the trained soil model and label encoder

model_path = os.path.join(os.path.dirname(__file__), 'models\\soil_crop_model.pkl')
with open(model_path, 'rb') as f:

    soil_model = pickle.load(f)

with open("ai/cv/models/soil_crop_labels.pkl", "rb") as f:
    crop_labels = pickle.load(f)

def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    """
    Predict the best crop for given soil parameters.
    
    Parameters:
        N, P, K: Nitrogen, Phosphorus, Potassium (int/float)
        temperature: °C (float)
        humidity: % (float)
        ph: soil pH (float)
        rainfall: mm (float)
        
    Returns:
        str: Predicted crop name
    """
    try:
        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        prediction = soil_model.predict(features)[0]
        crop_name = crop_labels[prediction]
        return crop_name
    except Exception as e:
        return f"Error in prediction: {str(e)}"

# Example usage:
if __name__ == "__main__":
    # Sample values
    result = predict_crop(90, 42, 43, 20.87, 82, 6.5, 202)
    print("Best crop to grow:", result)
