import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

print("Training Autonomous Agronomist Model...")

# GENERATE SYNTHETIC DATASET
# simulating 1000 readings.
# High Temp + Low Moisture = STRESSED (1)
# Low Temp + High Moisture = HEALTHY (0)

data_size = 1000

# Temperature (20C to 40C)
temps = np.random.uniform(20, 40, data_size)

# Soil Moisture (10% to 90%)
# In a real drone - Thermal/Multispectral
moisture = np.random.uniform(10, 90, data_size)

labels = []
for i in range(data_size):
    if temps[i] > 32 and moisture[i] < 45:
        labels.append(1) # Stressed
    elif temps[i] > 28 and moisture[i] < 30:
        labels.append(1) # Stressed
    else:
        labels.append(0) # Healthy

df = pd.DataFrame({'temp': temps, 'moisture': moisture, 'stress_label': labels})

X = df[['temp', 'moisture']]
y = df['stress_label']

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

print(f" Model Trained. Accuracy: {model.score(X, y)*100:.2f}%")

joblib.dump(model, 'crop_health_model.pkl')
print("Model saved to 'crop_health_model.pkl'")
