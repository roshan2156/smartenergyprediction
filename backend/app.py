from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
import bcrypt
import json
from datetime import datetime
import traceback

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ooLBypHDuxgxiRggXpupCdLMxKALCyEq@mainline.proxy.rlwy.net:25123/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

with app.app_context():
    db.create_all()

# ==================== DATA SCIENCE: PURE PYTHON ML ====================
class EnergyPredictor:
    """Custom Linear Regression built from scratch in pure Python"""
    def __init__(self):
        self.coefficients = []
        self.intercept = 0
        self.r_squared = 0

    def train(self, X, y):
        """Train using Least Squares Method"""
        if not X or not y: return False
        n = len(X)
        if n == 0: return False

        # Add bias term (intercept)
        X_bias = [[1] + row for row in X]
        
        # Transpose of X
        X_T = [[X_bias[j][i] for j in range(len(X_bias))] for i in range(len(X_bias[0]))]
        
        # Multiply X_T * X
        XT_X = [[sum(X_T[i][k] * X_bias[k][j] for k in range(n)) for j in range(len(X_bias[0]))] for i in range(len(X_T))]
        
        # Invert XT_X (Matrix inversion for small matrices)
        XT_X_inv = self.invert_matrix(XT_X)
        if not XT_X_inv: return False
            
        # Multiply XT_X_inv * X_T
        XT_X_inv_XT = [[sum(XT_X_inv[i][k] * X_T[k][j] for k in range(len(X_T))) for j in range(n)] for i in range(len(XT_X_inv))]
        
        # Multiply by y to get coefficients
        self.coefficients = [sum(XT_X_inv_XT[i][j] * y[j] for j in range(n)) for i in range(len(XT_X_inv_XT))]
        self.intercept = self.coefficients[0]
        self.coefficients = self.coefficients[1:]
        
        # Calculate R-squared (Accuracy metric)
        y_mean = sum(y) / len(y)
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        ss_res = sum((y[i] - self.predict(X[i])) ** 2 for i in range(len(y)))
        self.r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return True

    def predict(self, X_row):
        return self.intercept + sum(c * x for c, x in zip(self.coefficients, X_row))

    def invert_matrix(self, m):
        n = len(m)
        identity = [[float(i == j) for j in range(n)] for i in range(n)]
        for i in range(n):
            if m[i][i] == 0: return None
            f = m[i][i]
            for j in range(n): m[i][j] /= f; identity[i][j] /= f
            for k in range(n):
                if k != i:
                    f = m[k][i]
                    for j in range(n): m[k][j] -= f * m[i][j]; identity[k][j] -= f * identity[i][j]
        return identity

predictor = EnergyPredictor()

# ==================== HELPERS ====================
def check_peak_hour(hour):
    return "Yes (7-10 PM)" if 19 <= hour <= 22 else "No"

# ==================== AUTH ====================
@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.json
        password_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
        user = User(name=data['name'], email=data['email'], password_hash=password_hash, phone=data.get('phone'))
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

# ==================== DATA SCIENCE CSV PREDICTION ====================
@app.route('/api/batch_predict', methods=['POST'])
def batch_predict():
    try:
        data = request.json
        user_id = int(data.get("user_id"))
        records = data.get("records", [])

        # --- DATA PREPROCESSING ---
        # Extract Features (X) and Target (y)
        X_train = []
        y_train = []
        appliance_usage = {}
        hourly_usage = {}

        for r in records:
            power = float(r.get("power_consumption_W", 0))
            duration = float(r.get("usage_duration_minutes", 0))
            hour = int(r.get("hour", 12))
            temp = float(r.get("temperature_setting_C", 24))
            
            # Actual energy (Target)
            energy = (power * duration) / (1000 * 60)
            
            # Features for ML: [power, duration, hour, temp]
            X_train.append([power, duration, hour, temp])
            y_train.append(energy)

            # Aggregate stats for frontend charts
            app_name = r.get("appliance", "Unknown")
            appliance_usage[app_name] = appliance_usage.get(app_name, 0) + energy
            hourly_usage[hour] = hourly_usage.get(hour, 0) + energy

        # --- MACHINE LEARNING TRAINING ---
        is_trained = predictor.train(X_train, y_train)
        
        total_predicted_energy = 0
        predictions_list = []

        # --- MACHINE LEARNING PREDICTION ---
        for i, r in enumerate(records):
            features = X_train[i]
            actual_energy = y_train[i]
            
            if is_trained:
                # Predict using our trained Linear Regression Model
                predicted_energy = predictor.predict(features)
            else:
                # Fallback to simple math
                predicted_energy = actual_energy

            total_predicted_energy += predicted_energy
            predictions_list.append({"actual": actual_energy, "predicted": round(predicted_energy, 4)})

        # --- SAVE TO DB ---
        for r in records:
            energy = (float(r.get("power_consumption_W", 0)) * float(r.get("usage_duration_minutes", 0))) / (1000 * 60)
            pred = Prediction(
                user_id=user_id, mode_used="csv_ml", input_data=json.dumps(r),
                predicted_energy=energy, predicted_cost=energy * 7, carbon=energy * 0.82,
                peak_hour=check_peak_hour(int(r.get("hour", 12))), waste_detected="No waste",
                efficiency_score=80, alerts="[]", tips="[]", appliance_count=1
            )
            db.session.add(pred)
        db.session.commit()

        return jsonify({
            "success": True,
            "total_energy": round(total_predicted_energy, 2),
            "total_cost": round(total_predicted_energy * 7, 2),
            "total_carbon": round(total_predicted_energy * 0.82, 2),
            "appliance_usage": appliance_usage,
            "hourly_usage": hourly_usage,
            "data_science_metrics": {
                "model_used": "Linear Regression (Pure Python)",
                "r_squared_score": round(predictor.r_squared, 4), # Accuracy
                "features_used": ["Power (W)", "Duration (min)", "Hour", "Temp (C)"],
                "rows_analyzed": len(records),
                "sample_predictions": predictions_list[:5] # Show first 5 actual vs predicted
            }
        })

    except Exception as e:
        db.session.rollback()
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
