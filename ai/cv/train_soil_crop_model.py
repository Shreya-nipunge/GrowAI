import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

# Paths
base_dir = os.path.dirname(__file__)  # directory of this script
models_dir = os.path.join(base_dir, "models")
os.makedirs(models_dir, exist_ok=True)  # create models folder if not exists

dataset_path = os.path.join(base_dir, "../../project_root/datasets/Crop_recommendation.csv")
model_path = os.path.join(models_dir, "soil_crop_model.pkl")
labels_path = os.path.join(models_dir, "soil_crop_labels.pkl")

# Load dataset
print(f"📂 Loading dataset from: {dataset_path}")
df = pd.read_csv(dataset_path)
print(f"✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# Split features & labels
X = df.drop('label', axis=1)
y = df['label']

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# Train model
print("🤖 Training model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print("✅ Model trained successfully!")

# Save model
with open(model_path, "wb") as f:
    pickle.dump(model, f)

# Save label encoder
with open(labels_path, "wb") as f:
    pickle.dump(label_encoder.classes_, f)

print(f"💾 Model saved to: {model_path}")
print(f"💾 Labels saved to: {labels_path}")
