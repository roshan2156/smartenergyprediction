import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import r2_score
import joblib
import os

# ================= SETUP =================
os.makedirs('models', exist_ok=True)
print("🚀 Training Models...")

# ================= LOAD DATA =================
df = pd.read_csv("data/final_smart_energy_dataset.csv")

df = df.dropna().drop_duplicates()

# ================= TIME FEATURES =================
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
df['month'] = df['timestamp'].dt.month
df['day_of_year'] = df['timestamp'].dt.dayofyear

# ================= ENCODING =================
label_encoders = {}
categorical_cols = [
    'occupancy_status','appliance','device_status','room_location',
    'season','day_of_week','holiday','appliance_category'
]

for col in categorical_cols:
    le = LabelEncoder()
    df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

# ================= FEATURES =================
feature_cols = [
    'power_consumption_W',
    'usage_duration_minutes',
    'hour','month','day_of_year',
    'temperature_setting_C',
    'occupancy_status_encoded','appliance_encoded','device_status_encoded',
    'room_location_encoded','season_encoded','day_of_week_encoded',
    'holiday_encoded','appliance_category_encoded'
]

X = df[feature_cols]

# ================= TARGET =================
y_energy = df['energy_consumption_kWh']
y_cost = df['energy_cost_rs']
y_carbon = df['carbon_emission_kg']
y_peak = df['peak_hour_flag']

# ================= SPLIT =================
X_train, X_test, y_energy_train, y_energy_test = train_test_split(
    X, y_energy, test_size=0.2, random_state=42
)

# Align other targets
y_cost_train = y_cost.loc[X_train.index]
y_cost_test = y_cost.loc[X_test.index]

y_carbon_train = y_carbon.loc[X_train.index]
y_carbon_test = y_carbon.loc[X_test.index]

y_peak_train = y_peak.loc[X_train.index]
y_peak_test = y_peak.loc[X_test.index]

# ================= SCALING =================
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ================= MODELS =================
energy_model = RandomForestRegressor(n_estimators=150, random_state=42)
energy_model.fit(X_train_scaled, y_energy_train)

cost_model = RandomForestRegressor(n_estimators=100, random_state=42)
cost_model.fit(X_train_scaled, y_cost_train)

carbon_model = RandomForestRegressor(n_estimators=100, random_state=42)
carbon_model.fit(X_train_scaled, y_carbon_train)

peak_model = RandomForestClassifier(random_state=42)
peak_model.fit(X_train_scaled, y_peak_train)

# ================= SAVE =================
joblib.dump(energy_model, 'models/energy_model.pkl')
joblib.dump(cost_model, 'models/cost_model.pkl')
joblib.dump(carbon_model, 'models/carbon_model.pkl')
joblib.dump(peak_model, 'models/peak_model.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
joblib.dump(label_encoders, 'models/label_encoders.pkl')
joblib.dump(feature_cols, 'models/features.pkl')

print("✅ Training Complete!")

# ================= EVALUATION =================
y_pred_energy = energy_model.predict(X_test_scaled)
print("Energy R2 Score:", r2_score(y_energy_test, y_pred_energy))