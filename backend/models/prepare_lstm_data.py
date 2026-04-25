import pandas as pd

# Load original dataset
df = pd.read_csv("data/final_smart_energy_dataset.csv")

# Create timestamp
df['timestamp'] = pd.date_range(start='2026-01-01', periods=len(df), freq='H')

# Calculate energy
df['energy_consumption_kWh'] = (
    df['power_consumption_W'] * df['usage_duration_minutes']
) / (1000 * 60)

# Keep only required columns
df = df[['timestamp', 'energy_consumption_kWh']]

# Save new dataset
df.to_csv("data/lstm_ready_data.csv", index=False)

print("✅ LSTM dataset ready!")