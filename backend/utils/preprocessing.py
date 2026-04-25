import pandas as pd
import numpy as np
from datetime import datetime


# ================= TIME FEATURE EXTRACTION =================
def extract_time_features(df):
    """Extract time-based features from timestamp"""

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    df['hour'] = df['timestamp'].dt.hour
    df['month'] = df['timestamp'].dt.month
    df['day_of_month'] = df['timestamp'].dt.day
    df['day_of_year'] = df['timestamp'].dt.dayofyear
    df['week_of_year'] = df['timestamp'].dt.isocalendar().week

    # Safe day_of_week generation
    df['day_of_week'] = df['timestamp'].dt.day_name()

    # Weekend detection
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday']).astype(int)

    # Time segments
    df['is_morning'] = ((df['hour'] >= 6) & (df['hour'] <= 10)).astype(int)
    df['is_afternoon'] = ((df['hour'] >= 12) & (df['hour'] <= 16)).astype(int)
    df['is_evening_peak'] = ((df['hour'] >= 18) & (df['hour'] <= 22)).astype(int)
    df['is_night'] = ((df['hour'] >= 23) | (df['hour'] <= 5)).astype(int)

    return df


# ================= ENERGY CALCULATIONS =================
def calculate_energy(power_watts, duration_minutes):
    """Calculate energy consumption in kWh"""
    return round((power_watts * (duration_minutes / 60)) / 1000, 3)


def calculate_cost(energy_kwh, rate_per_kwh=7):
    """Calculate cost"""
    return round(energy_kwh * rate_per_kwh, 2)


def calculate_carbon(energy_kwh, carbon_factor=0.82):
    """Calculate carbon emission"""
    return round(energy_kwh * carbon_factor, 3)


# ================= APPLIANCE CATEGORY =================
def get_appliance_category(appliance):
    """Categorize appliances"""

    categories = {
        'AC': 'High',
        'Water Heater': 'High',
        'Washing Machine': 'Medium',
        'Fridge': 'Medium',
        'Microwave': 'Medium',
        'Iron': 'Medium',
        'Fan': 'Low',
        'Light': 'Low',
        'TV': 'Low',
        'Computer': 'Low'
    }

    return categories.get(appliance, 'Medium')


# ================= PEAK HOUR =================
def detect_peak_hour(hour):
    """Detect peak hours (7PM–10PM)"""
    return 1 if 19 <= hour <= 22 else 0


# ================= WASTE DETECTION =================
def detect_waste(device_status, occupancy, usage_minutes, appliance, hour):
    """Detect energy waste"""

    if device_status == "ON" and occupancy == "Vacant":
        return 1

    elif device_status == "ON" and usage_minutes > 180 and appliance in ["AC", "Water Heater"]:
        return 1

    elif device_status == "ON" and hour >= 23 and appliance in ["TV", "Light", "Fan"]:
        return 1

    return 0


# ================= TEST BLOCK =================
if __name__ == "__main__":

    print("🔧 Testing preprocessing functions...\n")

    # Sample inputs
    power = 1500
    duration = 60

    energy = calculate_energy(power, duration)
    cost = calculate_cost(energy)
    carbon = calculate_carbon(energy)

    print("⚡ Energy:", energy, "kWh")
    print("💰 Cost:", cost, "₹")
    print("🌱 Carbon:", carbon, "kg CO2")

    category = get_appliance_category("AC")
    print("🔌 Category:", category)

    peak = detect_peak_hour(20)
    print("⏰ Peak Hour:", peak)

    waste = detect_waste("ON", "Vacant", 200, "AC", 22)
    print("🚨 Waste Detected:", waste)