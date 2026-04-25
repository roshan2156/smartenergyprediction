import pandas as pd
import joblib
from datetime import datetime


class SmartEnergyPredictor:

    def __init__(self):
        # Load models
        self.energy_model = joblib.load('models/energy_model.pkl')
        self.cost_model = joblib.load('models/cost_model.pkl')
        self.carbon_model = joblib.load('models/carbon_model.pkl')
        self.peak_model = joblib.load('models/peak_model.pkl')
        self.waste_model = joblib.load('models/waste_model.pkl')

        # Load preprocessing tools
        self.scaler = joblib.load('models/scaler.pkl')
        self.label_encoders = joblib.load('models/label_encoders.pkl')
        self.features = joblib.load('models/features.pkl')

    # ================= MULTI-APPLIANCE =================
    def combine_appliances(self, appliances):
        total_power = 0
        total_duration = 0

        for a in appliances:
            power = a['power']
            duration = a['duration']
            qty = a['qty']

            total_power += power * qty
            total_duration += duration * qty  # ✅ FIXED

        return total_power, total_duration

    # ================= PREDICT =================
    def predict(self, input_data, appliances):

        # Combine appliances
        power, duration = self.combine_appliances(appliances)

        # Base features
        data = {
            'power_consumption_W': power,
            'usage_duration_minutes': duration,
            'hour': input_data.get('hour', datetime.now().hour),
            'month': datetime.now().month,
            'day_of_year': datetime.now().timetuple().tm_yday,
            'outside_temperature_C': input_data.get('outside_temperature_C', 30),
            'humidity_percent': input_data.get('humidity_percent', 60)
        }

        # Encode categorical features
        for col, encoder in self.label_encoders.items():
            val = input_data.get(col, 'Unknown')  # ✅ safer default
            try:
                data[col + '_encoded'] = encoder.transform([val])[0]
            except:
                data[col + '_encoded'] = 0  # fallback

        # Convert to DataFrame
        df = pd.DataFrame([data])

        # Ensure all features exist
        for f in self.features:
            if f not in df.columns:
                df[f] = 0

        X = df[self.features]
        X_scaled = self.scaler.transform(X)

        # Predictions
        energy = self.energy_model.predict(X_scaled)[0]
        cost = self.cost_model.predict(X_scaled)[0]
        carbon = self.carbon_model.predict(X_scaled)[0]
        peak = self.peak_model.predict(X_scaled)[0]
        waste = self.waste_model.predict(X_scaled)[0]

        return {
            "energy": round(float(energy), 3),
            "cost": round(float(cost), 2),
            "carbon": round(float(carbon), 3),
            "peak": bool(peak),
            "waste": bool(waste)
        }


# ================= TEST =================
if __name__ == "__main__":

    predictor = SmartEnergyPredictor()

    appliances = [
        {"power": 1500, "duration": 60, "qty": 1},
        {"power": 500, "duration": 30, "qty": 1}
    ]

    input_data = {
        "appliance": "AC",
        "occupancy_status": "Occupied",
        "room_location": "Living Room",
        "season": "Summer",
        "day_of_week": "Monday",
        "holiday": "No",
        "outside_temperature_C": 35,
        "humidity_percent": 60
    }

    result = predictor.predict(input_data, appliances)
    print("\n🔮 Prediction Result:")
    print(result)