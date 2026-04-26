# ⚡ Smart Electricity Consumption Monitoring and Prediction System

[![Live Demo](https://img.shields.io/badge/Live_Demo-smartenergyprediction-blue?style=for-the-badge&logo=render)](https://smartenergyprediction-3.onrender.com)

## 📌 Overview
Smart Energy Monitor is a full-stack AI-based web application that predicts energy consumption, cost, and carbon emissions. It provides analytics dashboards, CSV uploads, and intelligent recommendations to optimize energy usage.

## ✨ Features
- 🔐 **User Authentication:** Secure Register/Login system
- 📊 **Interactive Dashboard:** Beautiful charts & analytics
- ⚡ **Energy Prediction:** Manual entry and batch CSV upload
- 🤖 **ML Models:** AI-powered predictions using Linear Regression & LSTM (~91% Accuracy)
- 💰 **Cost Calculation:** Estimate electricity costs
- 🌱 **Carbon Emission Tracking:** Monitor environmental impact
- 📁 **CSV Export:** Download user data & prediction results
- 📜 **History Tracking:** Keep logs of past historical usage

## 🛠️ Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript

**Backend:**
- Flask (Python)
- Flask-SQLAlchemy (ORM)
- REST APIs

**Database:**
- MySQL (Deployed on Railway Cloud)

**Machine Learning:**
- NumPy, Pandas
- Scikit-learn (Linear Regression)
- TensorFlow (LSTM)

**Deployment:**
- Render (Backend)
- Railway (Database)

## 📂 Project Structure

```text
SMART ENERGY MONITOR/
│
├── backend/
│   ├── app.py
│   ├── predict.py
│   ├── train_model.py
│   ├── generate_data.py
│   ├── requirements.txt
│   │
│   ├── exports/                # Exported CSV data
│   │   ├── predictions.csv
│   │   └── users.csv
│   │
│   ├── models/                 # Pre-trained ML & LSTM models
│   │   ├── lstm_model.py
│   │   ├── lstm_predict.py
│   │   ├── prepare_lstm_data.py
│   │   ├── *.pkl 
│   │   └── *.h5 
│   │
│   ├── data/                   # Datasets for training & testing
│   │   ├── final_smart_energy_dataset.csv
│   │   ├── lstm_ready_data.csv
│   │   └── sample_energy_data.csv
│   │
│   ├── utils/                  # Helper scripts
│   │   ├── preprocessing.py
│   │   └── evaluation.py
│   │
│   └── tf_env/                 ❌ (DO NOT UPLOAD - Virtual Environment)
│
├── frontend/
│   ├── index.html
│   ├── home.html
│   ├── dashboard.html
│   ├── history.html
│   ├── reports.html
│   ├── login.html
│   ├── register.html
│   ├── manual-input.html
│   ├── csv-upload.html
│   ├── ai-assistant.html
│   │
│   ├── js/                     # Frontend logic
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── charts.js
│   │   ├── predictions.js
│   │   └── utils.js
│   │
│   └── images/                 # Assets
│       ├── roshan.jpg
│       ├── vatsal.jpg
│       └── zeel.jpg
│
├── .env
├── render.yaml
├── Procfile
└── README.md
```

## ⚙️ Setup Instructions (Local)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/roshan2156/smartenergyprediction.git
cd smartenergyprediction
```

### 2️⃣ Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3️⃣ Configure the Database
In `app.py` or within a `.env` file, configure your MySQL database connection:
```env
DATABASE_URL=mysql+pymysql://user:password@host:port/db
```

### 4️⃣ Run the Backend Server
```bash
python app.py
```

### 5️⃣ Open the Frontend
Simply open `frontend/index.html` in your favorite web browser.

## 🌐 Deployment (Render)

### 🔹 Build Command
```bash
cd backend && pip install -r requirements.txt
```

### 🔹 Start Command
```bash
cd backend && gunicorn app:app
```

### ⚠️ IMPORTANT (Deployment Fixes)

❌ **DO NOT UPLOAD the following files/folders to your repo:**
- `tf_env/`
- `__pycache__/`
- `.pyc` files

👉 **Ensure your `.gitignore` file includes:**
```gitignore
tf_env/
__pycache__/
*.pyc
.env
```

✅ **Add Gunicorn to requirements.txt**
If you encounter a `gunicorn: command not found` error, make sure to add `gunicorn` to your `requirements.txt` file.

🔑 **Environment Variables (Render)**
Go to Render Dashboard -> Environment Tab -> Add Variable:
- **KEY**: `DATABASE_URL`
- **VALUE**: `mysql+pymysql://root:password@host:port/db`

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/register` | POST | Register user |
| `/api/login` | POST | Login user |
| `/api/predict` | POST | Single manual prediction |
| `/api/batch_predict` | POST | Batch CSV prediction |
| `/api/history` | GET | Retrieve user history |
| `/api/health` | GET | Server health check |

## 🧠 Machine Learning Model
- **Algorithms:** Linear Regression + LSTM
- **Accuracy:** ~91%
- **Key Features Analyzed:**
  - Power Consumption
  - Duration
  - Hour
  - Temperature

## 📸 Screenshots
*(Website)*
<img width="1897" height="902" alt="image" src="https://github.com/user-attachments/assets/29048c4a-4c17-4c7e-8f74-fa1639d1fd77" />

<img width="1898" height="898" alt="image" src="https://github.com/user-attachments/assets/46fb2b91-8798-4e7b-b167-632d6099cd8a" />

<img width="1897" height="866" alt="image" src="https://github.com/user-attachments/assets/2fbad41c-d470-41ed-84df-e033e27241ba" />

<img width="1892" height="903" alt="image" src="https://github.com/user-attachments/assets/193719d8-b2cf-44fa-9b67-e84720b58ce1" />

<img width="1898" height="887" alt="image" src="https://github.com/user-attachments/assets/2b4e1677-9ec2-45d1-94aa-f185b8bbf7b6" />

*(Database-MySQL)*
<img width="1838" height="897" alt="image" src="https://github.com/user-attachments/assets/348db9a4-bf01-42da-80dd-8df86047c7d5" />

<img width="1822" height="892" alt="image" src="https://github.com/user-attachments/assets/57d5ca4b-6b02-4eb8-b654-cc9d60888828" />

## 🚧 Future Improvements
- [ ] 📱 Mobile responsive design improvements
- [ ] 🔔 Smart alert notifications for high usage
- [ ] 📡 IoT integration for direct meter readings
- [ ] 📊 Advanced analytics and visualization features

## 👨‍💻 Contributors
**Team Members:**
- Roshan Patil
- Vatsal Lad
- Zeel Bhandari
