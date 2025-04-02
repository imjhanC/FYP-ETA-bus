import pandas as pd
import joblib
import uvicorn
import requests
import datetime
import pytz
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import time
import firebase_admin
from firebase_admin import db, credentials
import holidays

# Initialize FastAPI app
app = FastAPI(title="Bus ETA Prediction API")

# Load the trained model
model = joblib.load('optimized_lightgbm_eta_predictor.pkl')

# Initialize Firebase
cred = credentials.Certificate("firebase.json")  # You need to create this file
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://fypbus-e8b65-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Malaysia holidays
my_holidays = holidays.Malaysia()

# Define input schema
class BusData(BaseModel):
    bus_id: str = "BUS_002"
    interval: int = 60  # seconds between predictions

# Helper functions
def is_holiday(date):
    """Check if the date is a holiday in Malaysia"""
    return date in my_holidays

def is_peak_hour(hour):
    """Check if the current hour is a peak hour"""
    return (6 <= hour < 9) or (16 <= hour < 20)

def get_day_of_week(date):
    """Get day of week as integer (0=Monday, 6=Sunday)"""
    return date.weekday()

def fetch_bus_data(bus_id):
    """Fetch real-time bus data from Firebase"""
    try:
        bus_ref = db.reference(f'/gps_data/{bus_id}')
        bus_data = bus_ref.get()
        return bus_data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def prepare_features(bus_data):
    """Transform raw bus data into model features"""
    if not bus_data:
        return None
    
    # Get current time in Malaysia
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
    now = datetime.datetime.now(malaysia_tz)
    
    # Process and prepare features
    features = {
        'current_stop_name': int(bus_data.get('current_stop_name', 0)),
        'next_stop_name': int(bus_data.get('next_stop_name', 0)),
        'day_of_week': get_day_of_week(now),
        'is_holiday': is_holiday(now.date()),
        'is_peak_hour': is_peak_hour(now.hour),
        'weather_condition': int(bus_data.get('weather_condition', 0)),
        'passenger_count': int(bus_data.get('passenger_count', 0)),
        'current_speed': float(bus_data.get('current_speed', 0)),
        'distance_to_next_stop': float(bus_data.get('distance_to_next_stop', 0)),
        'current_lat': float(bus_data.get('current_lat', 0)),
        'current_lon': float(bus_data.get('current_lon', 0))
    }
    
    return pd.DataFrame([features])

def make_prediction(input_df):
    """Make ETA prediction using the model"""
    if input_df is None:
        return None
    return model.predict(input_df)[0]

def send_prediction_to_firebase(bus_id, prediction):
    """Send prediction back to Firebase"""
    if prediction is None:
        return False
    
    try:
        # Get current time in Malaysia
        malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
        now = datetime.datetime.now(malaysia_tz)
        
        prediction_data = {
            'predicted_eta': round(float(prediction), 2),
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        pred_ref = db.reference(f'/predictions/{bus_id}')
        pred_ref.set(prediction_data)
        return True
    except Exception as e:
        print(f"Error sending prediction: {e}")
        return False

async def prediction_loop(bus_id, interval):
    """Continuous prediction loop"""
    while True:
        try:
            # Fetch current bus data
            bus_data = fetch_bus_data(bus_id)
            
            # Prepare features
            input_df = prepare_features(bus_data)
            
            # Make prediction
            prediction = make_prediction(input_df)
            
            # Send to Firebase
            if prediction is not None:
                success = send_prediction_to_firebase(bus_id, prediction)
                if success:
                    print(f"[{datetime.datetime.now()}] Prediction for {bus_id}: {prediction:.2f} minutes")
                else:
                    print(f"[{datetime.datetime.now()}] Failed to send prediction for {bus_id}")
            else:
                print(f"[{datetime.datetime.now()}] Could not make prediction for {bus_id}")
            
            # Wait for next interval
            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Error in prediction loop: {e}")
            await asyncio.sleep(interval)

# API endpoints
@app.post("/start_predictions")
async def start_predictions(data: BusData, background_tasks: BackgroundTasks):
    """Start the prediction loop for a bus"""
    import asyncio
    background_tasks.add_task(prediction_loop, data.bus_id, data.interval)
    return {"status": "success", "message": f"Started predictions for {data.bus_id}"}

@app.get("/predict/{bus_id}")
async def predict(bus_id: str):
    """Make a single prediction for a bus"""
    # Fetch current bus data
    bus_data = fetch_bus_data(bus_id)
    
    if not bus_data:
        return {"status": "error", "message": "Bus data not found"}
    
    # Prepare features
    input_df = prepare_features(bus_data)
    
    # Make prediction
    prediction = make_prediction(input_df)
    
    if prediction is None:
        return {"status": "error", "message": "Could not make prediction"}
    
    # Send to Firebase
    success = send_prediction_to_firebase(bus_id, prediction)
    
    return {
        "status": "success" if success else "error",
        "bus_id": bus_id,
        "predicted_eta": round(float(prediction), 2),
        "firebase_update": "success" if success else "failed"
    }

if __name__ == "__main__":
    import asyncio
    uvicorn.run("fastAPI:app", host="0.0.0.0", port=8000, reload=True)