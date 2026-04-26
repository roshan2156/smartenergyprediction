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

# ==================== DATABASE FIX ====================
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("📡 DATABASE URL:", os.getenv("DATABASE_URL"))

db = SQLAlchemy(app)

# ==================== INIT ====================
predictor = SmartEnergyPredictor()
lstm = LSTMPredictor()

EXPORTS_FOLDER = 'exports'
os.makedirs(EXPORTS_FOLDER, exist_ok=True)

# ==================== MODELS ====================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    mode_used = db.Column(db.String(50))
    input_data = db.Column(db.Text)
    predicted_energy = db.Column(db.Float)
    predicted_cost = db.Column(db.Float)
    carbon = db.Column(db.Float)
    peak_hour = db.Column(db.String(20))
    waste_detected = db.Column(db.Text)
    efficiency_score = db.Column(db.Float)
    alerts = db.Column(db.Text)
    tips = db.Column(db.Text)
    appliance_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ❌ REMOVED db.create_all()

# ==================== HELPERS ====================
def check_peak_hour(hour):
    return "Yes (7-10 PM)" if 19 <= hour <= 22 else "No"

# ==================== AUTH ====================
@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.json
        password_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()

        user = User(
            name=data['name'],
            email=data['email'],
            password_hash=password_hash,
            phone=data.get('phone')
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({"success": True, "user": {"id": user.id, "name": user.name}})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and bcrypt.checkpw(data['password'].encode(), user.password_hash.encode()):
        return jsonify({"success": True, "user": {"id": user.id, "name": user.name}})
    
    return jsonify({"success": False})

# ==================== PREDICT ====================
@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.json

        user_id = int(data.get("user_id"))
        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "error": "User not found"})

        power = float(data.get("power_consumption_W", 0))
        duration = float(data.get("usage_duration_minutes", 60))
        hour = int(data.get("hour", 12))

        energy = (power * duration) / (1000 * 60)
        cost = energy * 7
        carbon = energy * 0.82

        prediction = Prediction(
            user_id=user_id,
            mode_used="manual",
            input_data=json.dumps(data),
            predicted_energy=energy,
            predicted_cost=cost,
            carbon=carbon,
            peak_hour=check_peak_hour(hour),
            waste_detected="No waste",
            efficiency_score=80,
            alerts="[]",
            tips="[]",
            appliance_count=1
        )

        db.session.add(prediction)
        db.session.commit()

        return jsonify({
            "success": True,
            "energy": energy,
            "cost": cost,
            "carbon": carbon
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

# ==================== BATCH ====================
@app.route('/api/batch_predict', methods=['POST'])
def batch_predict():
    try:
        data = request.json
        user_id = int(data.get("user_id"))

        records = data.get("records", [])
        total_energy = 0

        for r in records:
            power = float(r.get("power_consumption_W", 0))
            duration = float(r.get("usage_duration_minutes", 0))

            energy = (power * duration) / (1000 * 60)
            total_energy += energy

            pred = Prediction(
                user_id=user_id,
                mode_used="csv",
                input_data=json.dumps(r),
                predicted_energy=energy,
                predicted_cost=energy * 7,
                carbon=energy * 0.82,
                peak_hour="No",
                waste_detected="No waste",
                efficiency_score=80,
                alerts="[]",
                tips="[]",
                appliance_count=1
            )

            db.session.add(pred)

        db.session.commit()

        return jsonify({"success": True, "total_energy": total_energy})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

# ==================== HISTORY ====================
@app.route('/api/history', methods=['GET'])
def history():
    try:
        user_id = int(request.args.get('user_id'))

        predictions = Prediction.query.filter_by(user_id=user_id).all()

        return jsonify({
            "success": True,
            "data": [
                {"energy": p.predicted_energy, "cost": p.predicted_cost}
                for p in predictions
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ==================== HEALTH ====================
@app.route('/api/health')
def health():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"status": "ok", "db": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)})

# ==================== FRONTEND ====================
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# ❌ NO app.run() (IMPORTANT for Render)
