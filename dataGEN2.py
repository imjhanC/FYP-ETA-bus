import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_bus_sequence_dataset(n_rows=100000):
    # Define the bus stops in sequence
    bus_stops = {
        1: {'name': 'Terminal Stop', 'coords': (3.0443577, 101.7947879)},
        2: {'name': 'Residential Area', 'coords': (3.0475698, 101.7962749)},
        3: {'name': 'Shopping District', 'coords': (3.0481001, 101.7983384)},
        4: {'name': 'Business Center', 'coords': (3.0481001, 101.7983384)},
        5: {'name': 'School Zone', 'coords': (3.0438577, 101.7979894)},
        6: {'name': 'Terminal Stop', 'coords': (3.0443577, 101.7947879)}  # Loop back to start
    }
    
    # Calculate distances between consecutive stops
    distances = {}
    for i in range(1, len(bus_stops)):
        lat1, lon1 = bus_stops[i]['coords']
        lat2, lon2 = bus_stops[i + 1]['coords']
        # Simple distance calculation (could be replaced with more accurate calculation)
        distance = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # Approximate km
        distances[i] = round(distance, 2)
    
    data = []
    current_time = datetime(2024, 1, 1, 6, 0)  # Start at 6 AM
    bus_id = 1
    
    while len(data) < n_rows:
        # Each bus completes the full circuit
        for sequence in range(1, len(bus_stops)):
            if len(data) >= n_rows:
                break
                
            current_stop = bus_stops[sequence]
            next_stop = bus_stops[sequence + 1]
            distance = distances[sequence]
            
            # Calculate realistic timing based on time of day
            hour = current_time.hour
            is_peak = (7 <= hour <= 9) or (17 <= hour <= 19)
            
            # Base speed varies by time of day
            base_speed = 20 if is_peak else 30  # km/h
            
            # Calculate ETA to next stop
            eta_minutes = int((distance / base_speed) * 60)
            
            # Add some random variation
            eta_minutes = int(eta_minutes * np.random.uniform(0.9, 1.1))
            
            data.append({
                'timestamp': current_time,
                'bus_id': f'BUS_{bus_id:03d}',
                'sequence_number': sequence,
                'current_stop_name': current_stop['name'],
                'current_stop_lat': current_stop['coords'][0],
                'current_stop_lon': current_stop['coords'][1],
                'next_stop_name': next_stop['name'],
                'next_stop_lat': next_stop['coords'][0],
                'next_stop_lon': next_stop['coords'][1],
                'distance_to_next_km': distance,
                'eta_minutes': eta_minutes
            })
            
            # Update time based on ETA plus dwell time at stop
            dwell_time = np.random.randint(1, 4)  # 1-3 minutes at each stop
            current_time += timedelta(minutes=eta_minutes + dwell_time)
        
        # After completing circuit, start with next bus or next day
        if current_time.hour >= 22:  # Last bus at 10 PM
            current_time = datetime(current_time.date() + timedelta(days=1), 6, 0)  # Next day 6 AM
            bus_id = 1
        else:
            bus_id += 1
    
    return pd.DataFrame(data)

# Generate and display sample data
df = generate_bus_sequence_dataset(100)
print("\nSample of the sequence-based dataset:")
print(df[['timestamp', 'bus_id', 'sequence_number', 'current_stop_name', 'next_stop_name', 'eta_minutes']].head(10))