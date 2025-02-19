import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_bus_dataset(n_rows=100000):
    np.random.seed(42)
    
    # Bus stops with their coordinates and names in sequence
    bus_stops = {
        1: {'name': 'UTAR bus stop', 'coords': (3.0443577, 101.7947879)},
        2: {'name': 'KJ370 Perumahan SG Long Seksyen 7', 'coords': (3.0475698, 101.7962749)},
        3: {'name': 'KJ428 SMK SG Long', 'coords': (3.0481001, 101.7983384)},
        4: {'name': 'Green Acre Condo', 'coords': (3.0438577, 101.7979894)},
        5: {'name': 'SG Long Club House', 'coords': (3.0414835, 101.7986407)},
    }
    
    # Calculate distances between consecutive stops
    distances = {}
    for i in range(1, len(bus_stops)):
        lat1, lon1 = bus_stops[i]['coords']
        lat2, lon2 = bus_stops[i + 1 if i < len(bus_stops) else 1]['coords']
        distance = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111
        distances[i] = round(distance, 2)
    
    # Add distance from last stop back to first stop
    lat1, lon1 = bus_stops[len(bus_stops)]['coords']
    lat2, lon2 = bus_stops[1]['coords']
    distances[len(bus_stops)] = round(np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111, 2)
    
    # Weather impact factors
    weather_conditions = {
        'sunny': {'speed_factor': 1.0, 'passenger_factor': 1.0},
        'rainy': {'speed_factor': 0.7, 'passenger_factor': 0.8},
        'storm': {'speed_factor': 0.4, 'passenger_factor': 0.3},
        'foggy': {'speed_factor': 0.6, 'passenger_factor': 0.7},
        'windy': {'speed_factor': 0.8, 'passenger_factor': 0.9}
    }
    
    # Traffic conditions with their impact factors
    traffic_conditions = {
        'normal': {'speed_factor': 1.0},
        'light': {'speed_factor': 1.2},
        'heavy': {'speed_factor': 0.6},
        'jam': {'speed_factor': 0.3}
    }
    
    # Initialize data dictionary
    data = {
        'timestamp': [], 'bus_id': [], 'route_id': [], 'stop_sequence': [],
        'current_stop_name': [], 'next_stop_name': [], 'day_of_week': [],
        'is_holiday': [], 'is_peak_hour': [], 'weather_condition': [],
        'passenger_count': [], 'current_speed': [], 'traffic_condition': [],
        'distance_to_next_stop': [], 'current_lat': [], 'current_lon': [],
        'eta_minutes': []
    }
    
    current_time = datetime(2024, 1, 1, 6, 0)
    bus_count = 5
    current_bus = 1
    current_sequence = 1
    
    while len(data['timestamp']) < n_rows:
        hour = current_time.hour
        day_of_week = current_time.weekday()
        
        if 6 <= hour <= 22:
            # Determine peak hours with more nuanced definition
            morning_peak = 7 <= hour <= 9
            evening_peak = 17 <= hour <= 19
            is_peak = (morning_peak or evening_peak) and day_of_week < 5
            
            # Weather probability changes based on time of day
            if 6 <= hour <= 10:  # Morning
                weather_probs = [0.5, 0.2, 0.05, 0.15, 0.1]  # More foggy in morning
            elif 14 <= hour <= 17:  # Afternoon
                weather_probs = [0.4, 0.3, 0.1, 0.05, 0.15]  # More rain/storms in afternoon
            else:
                weather_probs = [0.6, 0.2, 0.05, 0.05, 0.1]
                
            weather = np.random.choice(list(weather_conditions.keys()), p=weather_probs)
            
            # Traffic probabilities based on time and day
            if is_peak:
                traffic_probs = [0.1, 0.1, 0.4, 0.4]  # More congestion during peak
            elif day_of_week < 5:  # Weekday non-peak
                traffic_probs = [0.4, 0.3, 0.2, 0.1]
            else:  # Weekend
                traffic_probs = [0.5, 0.3, 0.15, 0.05]
                
            traffic = np.random.choice(list(traffic_conditions.keys()), p=traffic_probs)
            
            # Calculate passenger count with more variation
            base_passengers = 40 if morning_peak else 35 if evening_peak else 20
            if day_of_week >= 5:  # Weekend adjustment
                base_passengers *= 0.7
            
            # Apply weather impact on passengers
            weather_passenger_factor = weather_conditions[weather]['passenger_factor']
            passenger_count = int(np.random.normal(
                base_passengers * weather_passenger_factor,
                base_passengers * 0.2
            ))
            passenger_count = max(0, min(50, passenger_count))
            
            # Calculate speed with more realistic factors
            base_speed = 35 if is_peak else 45  # km/h
            weather_speed_factor = weather_conditions[weather]['speed_factor']
            traffic_speed_factor = traffic_conditions[traffic]['speed_factor']
            
            # Additional speed adjustments based on stop sequence
            # Slower near schools during school hours
            if current_sequence == 3 and 7 <= hour <= 14 and day_of_week < 5:
                base_speed *= 0.8
            
            current_speed = base_speed * weather_speed_factor * traffic_speed_factor
            current_speed = max(5, min(60, np.random.normal(current_speed, 3)))
            
            # Get current and next stop
            current_stop = bus_stops[current_sequence]
            next_sequence = current_sequence + 1 if current_sequence < len(bus_stops) else 1
            next_stop = bus_stops[next_sequence]
            
            # Calculate ETA with more factors
            distance = distances[current_sequence]
            base_eta = (distance / current_speed) * 60
            
            # Additional ETA factors
            eta_multiplier = 1.0
            if current_sequence == 3 and 7 <= hour <= 14 and day_of_week < 5:
                eta_multiplier *= 1.3  # School zone delay
            if is_peak:
                eta_multiplier *= 1.2
            
            eta = int(base_eta * eta_multiplier * np.random.normal(1, 0.1))
            
            # Calculate current position
            progress = np.random.random()
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
            if current_sequence == 1:
                current_bus = (current_bus % bus_count) + 1
            
            current_time += timedelta(minutes=5 + np.random.randint(0, 3))
        else:
            next_day = current_time.date() + timedelta(days=1)
            current_time = datetime.combine(next_day, datetime.min.time().replace(hour=6))
            current_sequence = 1
            current_bus = 1
    
    return pd.DataFrame(data)

# Generate and save the dataset
df = generate_bus_dataset(100000)
df.to_csv('bus_eta_dataset.csv', index=False)