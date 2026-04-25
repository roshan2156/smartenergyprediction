import numpy as np
import joblib
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os

class LSTMPredictor:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.model = load_model(os.path.join(BASE_DIR, "lstm_model.h5"))
        self.scaler = joblib.load(os.path.join(BASE_DIR, "lstm_scaler.pkl"))

    def forecast(self, last_values, days=30):
        result = []

        # Scale input
        data = self.scaler.transform(last_values.reshape(-1, 1))

        for _ in range(days):
            input_seq = data[-24:].reshape(1, 24, 1)

            pred = self.model.predict(input_seq, verbose=0)

            # ✅ FIX NaN
            if np.isnan(pred).any():
                pred = np.array([[0]])

            # ✅ STABILITY FIX
            pred = np.clip(pred, 0, 10)

            # Append prediction
            data = np.vstack((data, pred))

            # Inverse scale
            value = self.scaler.inverse_transform(pred)[0][0]
            result.append(value)

        return result


# ================= TEST BLOCK =================
if __name__ == "__main__":
    lstm = LSTMPredictor()

    # Sample last 24 hours data
    last_values = np.array([
        2.1, 2.3, 2.5, 2.7, 2.6, 2.4, 2.2, 2.3,
        2.6, 2.8, 3.0, 3.2, 3.1, 2.9, 2.7, 2.6,
        2.8, 3.0, 3.3, 3.5, 3.4, 3.2, 3.0, 2.8
    ])

    # 🔮 30-day prediction
    future = lstm.forecast(last_values, days=30)

    print("\n🔮 Predicted values:")
    print(future)

    print("\n⚡ Total Energy:")
    print(sum(future))

    # ================= GRAPH =================
    actual = last_values
    min_len = min(len(actual), len(future))

    plt.figure(figsize=(10, 5))
    plt.plot(range(len(actual)), actual, label="Actual")
    plt.plot(range(len(future)), future, label="Predicted")
    plt.legend()
    plt.title("Actual vs Predicted Energy")
    plt.xlabel("Days")
    plt.ylabel("Energy (kWh)")
    plt.show()

    # ================= ACCURACY =================
    rmse = np.sqrt(mean_squared_error(actual[:min_len], future[:min_len]))
    mae = mean_absolute_error(actual[:min_len], future[:min_len])

    print("\n📊 Accuracy Metrics:")
    print("RMSE:", rmse)
    print("MAE:", mae)

    # ================= 365-DAY FORECAST =================
    future_365 = lstm.forecast(last_values, days=365)

    plt.figure(figsize=(12, 5))
    plt.plot(future_365)
    plt.title("365-Day Energy Forecast")
    plt.xlabel("Days")
    plt.ylabel("Energy (kWh)")
    plt.show()