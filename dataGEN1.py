import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_bus_dataset(n_rows=100000):
    # Initialize random seed for reproducibility
    np.random.seed(42)
    
    # Bus stops with their coordinates and names in sequence
    bus_stops = {
        1: {'name': 'UTAR bus stop', 'coords': (3.0443577, 101.7947879)},
        2: {'name': 'KJ370 Perumahan SG Long Seksyen 7', 'coords': (3.0475698, 101.7962749)},
        3: {'name': 'KJ428 SMK SG Long', 'coords': (3.0481001, 101.7983384)},
        4: {'name': 'Green Acre Condo', 'coords': (3.0438577, 101.7979894)},
        5: {'name': 'SG Long Club House', 'coords': (3.0414835, 101.7986407)},  # Loop back to start
        #6: {'name': 'UTAR bus stop', 'coords': (3.0443577, 101.7947879)},
    }
    
    # Traffic signals and intersections
    traffic_signals = [(3.043144, 101.791667)]
    intersections = [
        (3.043144, 101.791667),
        (3.051489, 101.801884),
        (3.046175, 101.806535),
        (3.042367, 101.802206),
        (3.041806, 101.793143)
    ]
    
    # Calculate distances between consecutive stops
    distances = {}
    for i in range(1, len(bus_stops)):
        lat1, lon1 = bus_stops[i]['coords']
        lat2, lon2 = bus_stops[i + 1 if i < len(bus_stops) else 1]['coords']
        distance = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # Approximate km
        distances[i] = round(distance, 2)
    
    # Add distance from last stop back to first stop
    lat1, lon1 = bus_stops[len(bus_stops)]['coords']
    lat2, lon2 = bus_stops[1]['coords']
    distances[len(bus_stops)] = round(np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111, 2)
    
    # Generate base data
    data = {
        'timestamp': [],
        'bus_id': [],
        'route_id': [],
        'stop_sequence': [],
        'current_stop_name': [],
        'next_stop_name': [],
        'day_of_week': [],
        'is_holiday': [],
        'is_peak_hour': [],
        'weather_condition': [],
        'passenger_count': [],
        'current_speed': [],
        'traffic_condition': [],
        'distance_to_next_stop': [],
        'current_lat': [],
        'current_lon': [],
        'eta_minutes': []
    }
    
    # Generate timestamps covering a month
    current_time = datetime(2024, 1, 1, 6, 0)  # Start at 6 AM
    weather_conditions = ['sunny', 'rainy', 'storm', 'foggy', 'windy']
    traffic_conditions = ['normal', 'light', 'heavy', 'jam']
    
    bus_count = 5  # Number of buses in operation
    current_bus = 1
    current_sequence = 1
    
    while len(data['timestamp']) < n_rows:
        hour = current_time.hour
        day_of_week = current_time.weekday()
        
        # Only operate between 6 AM and 10 PM
        if 6 <= hour <= 22:
            # Determine peak hours (7-9 AM and 5-7 PM on weekdays)
            is_peak = (7 <= hour <= 9 or 17 <= hour <= 19) and day_of_week < 5
            
            # Generate conditions
            weather = np.random.choice(weather_conditions, p=[0.6, 0.2, 0.05, 0.05, 0.1])
            traffic = np.random.choice(traffic_conditions, 
                                     p=[0.2, 0.1, 0.4, 0.3] if is_peak else [0.4, 0.3, 0.2, 0.1])
            
            # Calculate passenger count
            base_passengers = 30 if is_peak else 15
            passenger_count = int(np.random.normal(base_passengers, 5))
            passenger_count = max(0, min(50, passenger_count))
            
            # Calculate speed based on conditions
            base_speed = 30 if is_peak else 40  # km/h
            if traffic == 'jam':
                base_speed *= 0.3
            elif traffic == 'heavy':
                base_speed *= 0.6
            elif traffic == 'light':
                base_speed *= 1.2
                
            if weather in ['storm', 'heavy_rain']:
                base_speed *= 0.7
                
            current_speed = max(5, min(60, np.random.normal(base_speed, 5)))
            
            # Get current and next stop
            current_stop = bus_stops[current_sequence]
            next_sequence = current_sequence + 1 if current_sequence < len(bus_stops) else 1
            next_stop = bus_stops[next_sequence]
            
            # Calculate ETA based on distance and conditions
            distance = distances[current_sequence]
            base_eta = (distance / base_speed) * 60  # minutes
            
            # Apply condition multipliers
            eta_multiplier = 1.0
            if traffic == 'jam':
                eta_multiplier *= 2.0
            elif traffic == 'heavy':
                eta_multiplier *= 1.5
            if weather in ['storm', 'heavy_rain']:
                eta_multiplier *= 1.3
            if is_peak:
                eta_multiplier *= 1.2
                
            eta = int(base_eta * eta_multiplier * np.random.normal(1, 0.1))
            
            # Calculate current position (interpolate between stops)
            progress = np.random.random()  # Progress between current and next stop
            current_lat = current_stop['coords'][0] + (next_stop['coords'][0] - current_stop['coords'][0]) * progress
            current_lon = current_stop['coords'][1] + (next_stop['coords'][1] - current_stop['coords'][1]) * progress
            
            # Populate data
            data['timestamp'].append(current_time)
            data['bus_id'].append(f'BUS_{current_bus:03d}')
            data['route_id'].append('R001')
            data['stop_sequence'].append(current_sequence)
            data['current_stop_name'].append(current_stop['name'])
            data['next_stop_name'].append(next_stop['name'])
            data['day_of_week'].append(day_of_week)
            data['is_holiday'].append(day_of_week >= 5)
            data['is_peak_hour'].append(is_peak)
            data['weather_condition'].append(weather)
            data['passenger_count'].append(passenger_count)
            data['current_speed'].append(round(current_speed, 2))
            data['traffic_condition'].append(traffic)
            data['distance_to_next_stop'].append(distance)
            data['current_lat'].append(round(current_lat, 6))
            data['current_lon'].append(round(current_lon, 6))
            data['eta_minutes'].append(eta)
            
            # Update sequence and bus
            current_sequence = next_sequence
            if current_sequence == 1:  # Completed a loop
                current_bus = (current_bus % bus_count) + 1
            
            # Add 5 minutes plus some random variation for the next entry
            current_time += timedelta(minutes=5 + np.random.randint(0, 3))
        else:
            # Skip to next day at 6 AM if outside operating hours
            next_day = current_time.date() + timedelta(days=1)
            current_time = datetime.combine(next_day, datetime.min.time().replace(hour=6))
            current_sequence = 1
            current_bus = 1
    
    return pd.DataFrame(data)

# Generate the dataset
df = generate_bus_dataset(100000)

# Save to CSV
df.to_csv('bus_eta_dataset.csv', index=False)

# Display first few rows and basic statistics
print("\nFirst few rows of the dataset:")
print(df[['timestamp', 'bus_id', 'stop_sequence', 'current_stop_name', 'next_stop_name', 'eta_minutes']].head(10))
print("\nBasic statistics:")
print(df.describe())