import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib
import os

os.makedirs("models", exist_ok=True)

print("🚀 Training LSTM Model...")

# ================= LOAD =================
df = pd.read_csv("data/final_smart_energy_dataset.csv")

# ✅ CLEAN FIRST
df = df.dropna()

# ✅ TIME SERIES FIX
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values(by='timestamp')

# ✅ GROUP (MOST IMPORTANT)
df = df.groupby('timestamp')['energy_consumption_kWh'].sum().reset_index()

# ✅ FINAL DATA
data = df[['energy_consumption_kWh']].values

# ================= SCALE =================
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

# ================= CREATE SEQUENCES =================
def create_sequences(data, time_steps=24):
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(data[i:i+time_steps])
        y.append(data[i+time_steps])
    return np.array(X), np.array(y)

X, y = create_sequences(scaled_data)

# ================= SPLIT =================
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# ================= MODEL =================
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(X.shape[1], 1)),
    LSTM(32),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse')

# ================= TRAIN =================
model.fit(X_train, y_train, epochs=30, batch_size=32)

# ================= SAVE (FIXED PATH) =================
model.save("models/lstm_model.h5")
joblib.dump(scaler, "models/lstm_scaler.pkl")

print("✅ LSTM Model Saved!")