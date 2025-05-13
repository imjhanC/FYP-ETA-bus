import pandas as pd
import joblib
import uvicorn
import requests
import datetime
import pytz
import asyncio
import re
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
    interval: int = 5  # seconds between predictions

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

def get_all_bus_ids():
    """Dynamically fetch all available bus IDs from Firebase"""
    try:
        gps_ref = db.reference('/gps_data')
        all_data = gps_ref.get()
        
        if not all_data:
            print("No bus data found in Firebase")
            return []
        
        # Filter for bus IDs matching pattern BUS_XXX
        bus_ids = [bus_id for bus_id in all_data.keys() if re.match(r'BUS_\d+', bus_id)]
        
        return bus_ids
    except Exception as e:
        print(f"Error fetching bus IDs: {e}")
        return []

def fetch_bus_data(bus_id):
    """Fetch real-time bus data from Firebase"""
    try:
        bus_ref = db.reference(f'/gps_data/{bus_id}')
        bus_data = bus_ref.get()
        return bus_data
    except Exception as e:
        print(f"Error fetching data for {bus_id}: {e}")
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
        print(f"Error sending prediction for {bus_id}: {e}")
        return False

async def process_single_bus(bus_id):
    """Process a single bus prediction cycle"""
    try:
        # Fetch current bus data
        bus_data = fetch_bus_data(bus_id)
        
        if not bus_data:
            print(f"[{datetime.datetime.now()}] No data found for {bus_id}")
            return
        
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
    except Exception as e:
        print(f"Error processing {bus_id}: {e}")

async def prediction_loop(interval):
    """Continuous prediction loop for all available buses"""
    while True:
        try:
            # Dynamically get all bus IDs
            bus_ids = get_all_bus_ids()
            
            if not bus_ids:
                print(f"[{datetime.datetime.now()}] No buses found in the database. Retrying in {interval} seconds.")
                await asyncio.sleep(interval)
                continue
                
            print(f"[{datetime.datetime.now()}] Processing buses: {', '.join(bus_ids)}")
            
            # Process each bus in parallel
            tasks = [process_single_bus(bus_id) for bus_id in bus_ids]
            await asyncio.gather(*tasks)
            
            # Wait for next interval
            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Error in prediction loop: {e}")
            await asyncio.sleep(interval)

# API endpoints
@app.post("/start_predictions")
async def start_predictions(data: BusData, background_tasks: BackgroundTasks):
    """Start the prediction loop for all available buses"""
    background_tasks.add_task(prediction_loop, data.interval)
    return {
        "status": "success", 
        "message": f"Started predictions for all available buses with {data.interval}-second interval"
    }

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

@app.get("/buses")
async def list_buses():
    """List all available buses in the system"""
    bus_ids = get_all_bus_ids()
    return {
        "status": "success",
        "count": len(bus_ids),
        "buses": bus_ids
    }

@app.on_event("startup")
async def startup_event():
    """Automatically start predictions for all buses when the app starts"""
    interval = 5  # 5 seconds between predictions
    
    # Start the prediction loop in the background
    asyncio.create_task(prediction_loop(interval))
    print(f"[{datetime.datetime.now()}] Automatic prediction started for all available buses")

if __name__ == "__main__":
    uvicorn.run("fastAPI1:app", host="0.0.0.0", port=8000, reload=True)

# cd Playground\FASTAPI
# uvicorn fastAPI1:app --host 0.0.0.0 --port 8000 --reload