from predict import SmartEnergyPredictor
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
import csv
import bcrypt
import json
from datetime import datetime
import traceback
from models.lstm_predict import LSTMPredictor
import numpy as np 

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize predictor
predictor = SmartEnergyPredictor()
lstm = LSTMPredictor()

# ==================== MYSQL DATABASE ====================
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ooLBypHDuxgxiRggXpupCdLMxKALCyEq@mainline.proxy.rlwy.net:25123/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Create exports folder
EXPORTS_FOLDER = 'exports'
os.makedirs(EXPORTS_FOLDER, exist_ok=True)
print(f"📁 CSV exports folder created: {os.path.abspath(EXPORTS_FOLDER)}/")

# ==================== MODELS ====================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    mode_used = db.Column(db.String(50))
    input_data = db.Column(db.Text)
    predicted_energy = db.Column(db.Float, nullable=False)
    predicted_cost = db.Column(db.Float, nullable=False)
    carbon = db.Column(db.Float, nullable=False)
    peak_hour = db.Column(db.String(20))
    waste_detected = db.Column(db.Text)
    efficiency_score = db.Column(db.Float)
    alerts = db.Column(db.Text)
    tips = db.Column(db.Text)
    appliance_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    print("✅ MySQL Database tables created/verified!")

# ==================== CSV FILE PATHS ====================
USERS_CSV = os.path.join(EXPORTS_FOLDER, 'users.csv')
PREDICTIONS_CSV = os.path.join(EXPORTS_FOLDER, 'predictions.csv')

def init_csv_files():
    try:
        if not os.path.exists(USERS_CSV):
            with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Created At'])
            print(f"✅ Created users CSV: {USERS_CSV}")
        
        if not os.path.exists(PREDICTIONS_CSV):
            with open(PREDICTIONS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Prediction ID', 'User ID', 'User Name', 'Mode Used',
                    'Energy (kWh)', 'Cost (Rs)', 'Carbon (kg CO2)',
                    'Peak Hour', 'Waste Detected', 'Efficiency Score',
                    'Appliance Count', 'Created At'
                ])
            print(f"✅ Created predictions CSV: {PREDICTIONS_CSV}")
    except Exception as e:
        print(f"❌ Error creating CSV files: {e}")

init_csv_files()

# ==================== HELPER FUNCTIONS ====================

def get_season(month):
    if month in [3, 4, 5]: return "Summer"
    elif month in [6, 7, 8]: return "Monsoon"
    elif month in [9, 10]: return "Autumn"
    elif month in [11, 12]: return "Winter"
    else: return "Spring"

def check_peak_hour(hour):
    return "Yes (7-10 PM)" if 19 <= hour <= 22 else "No"

def detect_waste(occupancy, energy):
    if occupancy == 'Vacant' and energy > 0.5:
        return "Appliances running while vacant", ["🗑️ Waste detected: Appliances running in vacant room"]
    elif energy > 5:
        return "High consumption detected", ["⚠️ High energy consumption detected"]
    return "No waste", []

def calculate_efficiency_score(energy, count, hours):
    if count == 0 or hours == 0:
        return 70
    expected = count * 0.8 * hours
    if expected == 0:
        return 70
    efficiency = max(0, min(100, (1 - energy/expected) * 100))
    return round(efficiency, 2)

def generate_tips(energy, efficiency_score, waste_detected, peak_hour):
    tips = []
    if energy > 5:
        tips.append("💡 High energy consumption detected. Consider reducing usage.")
    if efficiency_score < 50:
        tips.append("💡 Low efficiency score. Replace old appliances with energy-efficient ones.")
    if waste_detected and waste_detected != "No waste":
        tips.append("💡 Energy waste detected! Turn off appliances when not in use.")
    if peak_hour == "Yes (7-10 PM)":
        tips.append("💡 Using appliances during peak hours increases cost. Shift to off-peak hours.")
    if energy <= 2:
        tips.append("🌟 Excellent! You're using energy efficiently.")
    if not tips:
        tips.append("✅ Good energy usage. Keep it up!")
    return tips

def save_user_to_csv(user):
    try:
        file_exists = os.path.exists(USERS_CSV)
        with open(USERS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or os.path.getsize(USERS_CSV) == 0:
                writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Created At'])
            writer.writerow([user.id, user.name, user.email, user.phone or '', user.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        print(f"✅ User saved to CSV: {user.email}")
        return True
    except Exception as e:
        print(f"❌ Error saving user to CSV: {e}")
        return False

def save_prediction_to_csv(prediction, user_name):
    try:
        file_exists = os.path.exists(PREDICTIONS_CSV)
        with open(PREDICTIONS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or os.path.getsize(PREDICTIONS_CSV) == 0:
                writer.writerow(['Prediction ID', 'User ID', 'User Name', 'Mode Used', 'Energy (kWh)', 'Cost (Rs)', 'Carbon (kg CO2)', 'Peak Hour', 'Waste Detected', 'Efficiency Score', 'Appliance Count', 'Created At'])
            writer.writerow([prediction.id, prediction.user_id or 'Guest', user_name, prediction.mode_used, prediction.predicted_energy, prediction.predicted_cost, prediction.carbon, prediction.peak_hour, prediction.waste_detected, prediction.efficiency_score, prediction.appliance_count, prediction.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        print(f"✅ Prediction saved to CSV: {user_name} - {prediction.predicted_energy} kWh")
        return True
    except Exception as e:
        print(f"❌ Error saving prediction to CSV: {e}")
        return False

# ==================== CSV EXPORT ENDPOINTS ====================

@app.route('/api/export/download/users', methods=['GET'])
def download_users_csv():
    try:
        if os.path.exists(USERS_CSV):
            return send_from_directory(EXPORTS_FOLDER, 'users.csv', as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'Users CSV file not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/download/predictions', methods=['GET'])
def download_predictions_csv():
    try:
        if os.path.exists(PREDICTIONS_CSV):
            return send_from_directory(EXPORTS_FOLDER, 'predictions.csv', as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'Predictions CSV file not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/refresh/users', methods=['POST'])
def refresh_users_csv():
    try:
        users = User.query.all()
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Created At'])
            for user in users:
                writer.writerow([user.id, user.name, user.email, user.phone or '', user.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        return jsonify({'success': True, 'message': f'Users CSV refreshed with {len(users)} records'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/refresh/predictions', methods=['POST'])
def refresh_predictions_csv():
    try:
        predictions = Prediction.query.all()
        with open(PREDICTIONS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Prediction ID', 'User ID', 'User Name', 'Mode Used', 'Energy (kWh)', 'Cost (Rs)', 'Carbon (kg CO2)', 'Peak Hour', 'Waste Detected', 'Efficiency Score', 'Appliance Count', 'Created At'])
            for pred in predictions:
                user = User.query.get(pred.user_id) if pred.user_id else None
                user_name = user.name if user else 'Guest User'
                writer.writerow([pred.id, pred.user_id or 'Guest', user_name, pred.mode_used, pred.predicted_energy, pred.predicted_cost, pred.carbon, pred.peak_hour, pred.waste_detected, pred.efficiency_score, pred.appliance_count, pred.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        return jsonify({'success': True, 'message': f'Predictions CSV refreshed with {len(predictions)} records'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/list', methods=['GET'])
def list_csv_files():
    try:
        files = []
        for filename in os.listdir(EXPORTS_FOLDER):
            if filename.endswith('.csv'):
                filepath = os.path.join(EXPORTS_FOLDER, filename)
                stat = os.stat(filepath)
                files.append({'filename': filename, 'size_kb': round(stat.st_size / 1024, 2), 'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')})
        return jsonify({'success': True, 'folder': os.path.abspath(EXPORTS_FOLDER), 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== API ENDPOINTS ====================

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.json
        print(f"📥 Registration data received: {data}")
        
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not name or not email or not password:
            return jsonify({'success': False, 'error': 'Name, email, and password are required'}), 400
        
        phone = data.get('phone', '')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Email already registered!'}), 400
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(name=name, email=email, password_hash=password_hash, phone=phone)
        
        db.session.add(new_user)
        db.session.commit()
        print(f"✅ User saved to MySQL: {email} (ID: {new_user.id})")
        
        save_user_to_csv(new_user)
        
        return jsonify({'success': True, 'message': 'Registration successful!', 'user': {'id': new_user.id, 'name': new_user.name, 'email': new_user.email}})
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in registration: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({"success": True, "user": {"id": user.id, "name": user.name, "email": user.email}})

    return jsonify({"success": False, "message": "Invalid credentials"})

# ==================== FIXED PREDICT ENDPOINT ====================

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.json
        
        # ✅ FIX 1: DEBUG LOG
        print("📥 PREDICT DATA RECEIVED:", data)
        print("👤 RAW USER ID:", data.get('user_id'), "TYPE:", type(data.get('user_id')))
        
        # ✅ FIX 2: CONVERT USER_ID TO INT
        user_id = data.get('user_id')
        
        if user_id is None or user_id == 'null' or user_id == '':
            print("❌ USER ID IS NULL")
            return jsonify({"success": False, "error": "User not logged in"}), 400
        
        try:
            user_id = int(user_id)
            print("✅ CONVERTED USER ID:", user_id, "TYPE:", type(user_id))
        except (ValueError, TypeError) as e:
            print(f"❌ INVALID USER ID TYPE: {e}")
            return jsonify({"success": False, "error": f"Invalid User ID format: {user_id}"}), 400
        
        # ✅ FIX 3: VERIFY USER EXISTS
        user = User.query.get(user_id)
        if not user:
            print(f"❌ USER NOT FOUND IN DB FOR ID: {user_id}")
            return jsonify({"success": False, "error": f"User not found with ID: {user_id}"}), 400
        
        print(f"✅ USER FOUND: {user.name} (ID: {user.id})")
        
        user_name = user.name
        mode = data.get('mode', 'manual')

        power = float(data.get('power_consumption_W', 0))
        duration = float(data.get('usage_duration_minutes', 60))
        occupancy = data.get('occupancy_status', 'Occupied')
        hour = int(data.get("hour", datetime.now().hour))
        appliance_count = int(data.get('appliance_count', 1))

        appliances = [{"power": power, "duration": duration, "qty": appliance_count}]
        season = get_season(datetime.now().month)

        ml_input = {
            "appliance": data.get("appliance", "AC"),
            "occupancy_status": occupancy,
            "room_location": data.get("room_location", "Living Room"),
            "season": season,
            "day_of_week": datetime.now().strftime("%A"),
            "holiday": "No",
            "hour": hour,
            "outside_temperature_C": float(data.get("temperature_setting_C", 24)),
            "humidity_percent": 60
        }

        # ✅ FIX 4: WRAP PREDICTION IN TRY-CATCH
        try:
            result = predictor.predict(ml_input, appliances)
            print(f"✅ ML PREDICTION RESULT: {result}")
        except Exception as ml_error:
            print(f"❌ ML PREDICTION ERROR: {ml_error}")
            traceback.print_exc()
            energy = (power * duration) / (1000 * 60)
            result = {"energy": energy, "cost": energy * 7, "carbon": energy * 0.82}

        # ================= LSTM FORECAST =================
        forecast_period = int(data.get("forecast_period", 1))
        
        try:
            if forecast_period > 1:
                last_values = np.array([result["energy"]] * 24)
                future = lstm.forecast(last_values, forecast_period)

                if future is not None and len(future) > 0 and not np.isnan(future).any():
                    future = np.array(future)
                    energy = float(np.sum(future))
                else:
                    energy = result["energy"]
            else:
                energy = result["energy"]
        except Exception as e:
            print("⚠️ LSTM ERROR (using fallback):", e)
            energy = result["energy"]

        cost = energy * 7
        carbon = energy * 0.82

        # ================= POST PROCESS =================
        peak_hour = check_peak_hour(hour)
        waste_detected, waste_alerts = detect_waste(occupancy, energy)
        efficiency_score = calculate_efficiency_score(energy, appliance_count, duration / 60)
        tips = generate_tips(energy, efficiency_score, waste_detected, peak_hour)

        # ✅ FIX 5: CREATE PREDICTION WITH EXPLICIT user_id
        prediction = Prediction(
            user_id=user_id,  
            mode_used=mode,
            input_data=json.dumps(data),
            predicted_energy=round(energy, 4),
            predicted_cost=round(cost, 2),
            carbon=round(carbon, 4),
            peak_hour=peak_hour,
            waste_detected=waste_detected,
            efficiency_score=efficiency_score,
            alerts=json.dumps(waste_alerts),
            tips=json.dumps(tips),
            appliance_count=appliance_count
        )

        # ✅ FIX 6: EXPLICIT COMMIT WITH ERROR HANDLING
        try:
            db.session.add(prediction)
            db.session.commit()
            print(f"✅ PREDICTION SAVED TO DB - ID: {prediction.id}, User: {user_id}, Energy: {energy}")
        except Exception as db_error:
            db.session.rollback()
            print(f"❌ DATABASE SAVE ERROR: {db_error}")
            traceback.print_exc()
            return jsonify({
                "success": True, "energy": energy, "cost": cost, "carbon": carbon,
                "peak_hour": peak_hour, "waste_detected": waste_detected != "No waste",
                "efficiency_score": efficiency_score, "alerts": waste_alerts,
                "recommendations": tips, "db_saved": False, "db_error": str(db_error)
            })

        # ✅ FIX 7: SAVE TO CSV
        try:
            save_prediction_to_csv(prediction, user_name)
        except Exception as csv_error:
            print(f"⚠️ CSV SAVE ERROR: {csv_error}")

        return jsonify({
            "success": True, "energy": energy, "cost": cost, "carbon": carbon,
            "peak_hour": peak_hour, "waste_detected": waste_detected != "No waste",
            "efficiency_score": efficiency_score, "alerts": waste_alerts,
            "recommendations": tips, "prediction_id": prediction.id, "db_saved": True
        })

    except Exception as e:
        db.session.rollback()
        print("❌ MAIN PREDICT ERROR:", e)
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/api/batch_predict', methods=['POST'])
def batch_predict():
    try:
        data = request.json
        print("📥 DATA RECEIVED:", data)
        print("👤 USER ID:", data.get("user_id"))

        user_id = data.get("user_id")
        try:
            user_id = int(user_id)
        except:
            user_id = None
            
        if not user_id:
            return jsonify({"success": False, "error": "User ID required"}), 400

        records = data.get("records", [])
        total_energy = 0
        total_cost = 0
        total_carbon = 0
        appliance_usage = {}
        hourly_usage = {}

        for r in records:
            power = float(r.get("power_consumption_W", 0))
            duration = float(r.get("usage_duration_minutes", 0))
            hour = int(r.get("hour", 12))

            energy = (power * duration) / (1000 * 60)
            cost = energy * 7
            carbon = energy * 0.82

            total_energy += energy
            total_cost += cost
            total_carbon += carbon

            appliance = r.get("appliance", "Unknown")
            appliance_usage[appliance] = appliance_usage.get(appliance, 0) + energy
            hourly_usage[hour] = hourly_usage.get(hour, 0) + energy
            
            prediction = Prediction(
                user_id=user_id if user_id else None, mode_used="csv",
                input_data=json.dumps(r), predicted_energy=energy, predicted_cost=cost,
                carbon=carbon, peak_hour=check_peak_hour(hour), waste_detected="No waste",
                efficiency_score=80, alerts=json.dumps([]), tips=json.dumps([]), appliance_count=1
            )
            db.session.add(prediction)

        db.session.commit()
        print("✅ Batch predictions saved in DB")

        return jsonify({
            "success": True, "total_energy": round(total_energy, 2),
            "total_cost": round(total_cost, 2), "total_carbon": round(total_carbon, 2),
            "appliance_usage": appliance_usage, "hourly_usage": hourly_usage
        })

    except Exception as e:
        db.session.rollback()
        print("❌ ERROR:", e)
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/api/history', methods=['GET'])
def api_history():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.created_at.desc()).all()
        
        result = []
        for pred in predictions:
            result.append({
                'id': pred.id, 'mode': pred.mode_used, 'timestamp': pred.created_at.isoformat(),
                'energy_kwh': pred.predicted_energy, 'cost_rs': pred.predicted_cost,
                'carbon_kg': pred.carbon, 'peak_hour': pred.peak_hour,
                'waste_detected': pred.waste_detected, 'efficiency_score': pred.efficiency_score
            })
        
        return jsonify({'success': True, 'predictions': result})
    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    try:
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {e}'
    return jsonify({'status': 'healthy', 'database': db_status, 'timestamp': datetime.now().isoformat()})

# ==================== DEBUG ENDPOINT ====================
@app.route('/api/debug/test-db', methods=['GET'])
def debug_test_db():
    try:
        user = User.query.first()
        if not user:
            return jsonify({"error": "No users in database. Register first!"})
        
        test_pred = Prediction(
            user_id=user.id, mode_used="test", input_data='{"test": true}',
            predicted_energy=1.5, predicted_cost=10.5, carbon=1.23,
            peak_hour="No", waste_detected="No waste", efficiency_score=85,
            alerts="[]", tips="[]", appliance_count=1
        )
        
        db.session.add(test_pred)
        db.session.commit()
        saved = Prediction.query.get(test_pred.id)
        
        return jsonify({
            "success": True, "message": "Database insertion works!",
            "user_id": user.id, "prediction_id": test_pred.id,
            "saved_energy": saved.predicted_energy if saved else None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()})

# ==================== FRONTEND ROUTES ====================
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    print("="*60)
    print("🚀 SMART ENERGY MONITOR BACKEND (MySQL + CSV)")
    print("="*60)
    print(f"📁 Database: MySQL (Railway)")
    print(f"📁 CSV Files Folder: {os.path.abspath(EXPORTS_FOLDER)}/")
    print("="*60)
    
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            print("✅ MySQL Database connected successfully!")
    except Exception as e:
        print(f"❌ MySQL Connection Error: {e}")
    
    app.run()