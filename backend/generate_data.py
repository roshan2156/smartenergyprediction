import csv
import random
from datetime import datetime, timedelta
import os

# Create data directory
os.makedirs('data', exist_ok=True)

print("="*60)
print("🚀 SMART ELECTRICITY SYSTEM - DATA GENERATION")
print("="*60)

# Configuration
rate_per_unit = 7  # ₹ per kWh
carbon_factor = 0.82  # kg CO2 per kWh

# Appliances with power and category
appliances = [
    ("AC", 1500, "High", "Cooling"),
    ("Fan", 70, "Low", "Ventilation"),
    ("Light", 40, "Low", "Lighting"),
    ("Fridge", 200, "Medium", "Cooling"),
    ("Washing Machine", 500, "Medium", "Laundry"),
    ("TV", 100, "Low", "Entertainment"),
    ("Microwave", 1200, "Medium", "Cooking"),
    ("Water Heater", 2000, "High", "Heating"),
    ("Iron", 1000, "Medium", "Clothing"),
    ("Computer", 150, "Low", "Work")
]

rooms = ["Living Room", "Bedroom", "Kitchen", "Hall", "Study Room", "Dining Room"]
occupancies = ["Occupied", "Vacant", "Partial"]
holidays = ["No", "Yes"]
seasons = ["Winter", "Summer", "Monsoon", "Autumn", "Spring"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weather_conditions = ["Normal", "Hot", "Cold", "Rainy", "Cloudy"]

print("\n📁 Generating Smart Electricity Dataset with 20,000 records...")

with open("data/final_smart_energy_dataset.csv", "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "timestamp", "home_id", "energy_consumption_kWh",
        "power_consumption_W", "voltage", "current",
        "temperature_setting_C", "occupancy_status", "appliance",
        "usage_duration_minutes", "device_status", "room_location",
        "season", "day_of_week", "hour_of_day", "holiday",
        "peak_hour_flag", "appliance_category", "appliance_type",
        "weather_condition", "outside_temperature_C", "humidity_percent",
        "energy_cost_rs", "carbon_emission_kg", "waste_flag"
    ])

    start_time = datetime(2024, 1, 1, 0, 0)

    for i in range(20000):
        dt = start_time + timedelta(minutes=i * 30)  # 30-minute intervals
        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        month = dt.month
        
        # Day type and season logic
        day_of_week = days[i % 7]
        season = seasons[(month - 1) // 3]  # Season based on month
        holiday = "Yes" if day_of_week in ["Saturday", "Sunday"] and random.random() > 0.7 else "No"
        
        # Weather based on season and hour
        if season == "Summer":
            outside_temp = random.choice([32, 34, 36, 38, 40])
            weather = random.choice(["Hot", "Normal"]) if hour < 18 else random.choice(["Normal", "Warm"])
        elif season == "Winter":
            outside_temp = random.choice([12, 14, 16, 18, 20])
            weather = random.choice(["Cold", "Normal"])
        else:
            outside_temp = random.choice([22, 24, 26, 28])
            weather = random.choice(["Normal", "Rainy", "Cloudy"])
        
        humidity = random.randint(40, 85)
        
        home_id = f"H{random.randint(1, 200):03d}"
        app, powerW, cat, app_type = random.choice(appliances)
        
        # Select random room location
        room_location = random.choice(rooms)
        
        # Usage patterns based on time of day
        if 6 <= hour <= 9:  # Morning
            usage_minutes = random.choice([15, 30, 45, 60])
            occupancy = "Occupied" if random.random() > 0.2 else "Partial"
        elif 12 <= hour <= 14:  # Lunch
            usage_minutes = random.choice([30, 45, 60])
            occupancy = "Occupied"
        elif 18 <= hour <= 22:  # Evening peak
            usage_minutes = random.choice([60, 90, 120, 150, 180])
            occupancy = "Occupied"
            # Higher chance of high-power appliances during peak
            if random.random() > 0.3:
                app, powerW, cat, app_type = random.choice([a for a in appliances if a[2] in ["High", "Medium"]])
        else:  # Night/Off-peak
            usage_minutes = random.choice([0, 15, 30, 45, 60, 120])
            occupancy = "Vacant" if random.random() > 0.6 else "Occupied"
        
        device_status = "ON" if random.random() > 0.15 else "OFF"
        if usage_minutes == 0:
            device_status = "OFF"
            energy_kwh = 0
        else:
            # Energy calculation (TARGET)
            energy_kwh = round((powerW * (usage_minutes / 60)) / 1000, 2)
        
        voltage = random.choice([220, 230, 240])
        current = round(powerW / voltage, 2) if powerW > 0 else 0
        tempC = random.choice([18, 20, 22, 24, 26, 28, 30])
        
        # Peak hour detection (7PM-10PM)
        peak_flag = 1 if 19 <= hour <= 22 else 0
        
        # Waste detection logic
        waste_flag = 0
        if device_status == "ON" and occupancy == "Vacant":
            waste_flag = 1
        elif device_status == "ON" and usage_minutes > 180 and app in ["AC", "Water Heater"]:
            waste_flag = 1
        elif device_status == "ON" and hour >= 23 and app in ["TV", "Light", "Fan"]:
            waste_flag = 1
        
        energy_cost = round(energy_kwh * rate_per_unit, 2)
        carbon_emission = round(energy_kwh * carbon_factor, 2)
        
        row = [
            timestamp, home_id, energy_kwh, powerW, voltage, current,
            tempC, occupancy, app, usage_minutes, device_status,
            room_location, season, day_of_week, hour, holiday,
            peak_flag, cat, app_type, weather, outside_temp, humidity,
            energy_cost, carbon_emission, waste_flag
        ]
        
        # Add missing values (0.5% of data)
        if random.random() < 0.005:
            missing_col = random.randrange(len(row))
            row[missing_col] = ""
        
        writer.writerow(row)
        
        if (i + 1) % 5000 == 0:
            print(f"✓ Generated {i + 1} records...")

print("\n✅ FINAL CLEAN DATASET GENERATED")
print(f"📁 Location: data/final_smart_energy_dataset.csv")
print(f"📊 Total Records: 20,000")
print(f"📈 Features: 25 columns including all required metrics")