import numpy as np
from sklearn.ensemble import IsolationForest

def generate_sensor_data(num_points=100, base_temp=25):
    """
    Generates synthetic sensor data based on a base temperature.
    
    Args:
        num_points (int): Number of data points to generate.
        base_temp (float): The base temperature to center the data around.
        
    Returns:
        list: A list of generated temperature readings.
    """
    # Generate data with some noise around the base temperature
    # We increase variance slightly if the temperature is extreme for realism, but keeping it simple for now
    noise = np.random.normal(0, 5, num_points)
    data = base_temp + noise
    return data.tolist()

def detect_anomalies(data, contamination=0.1):
    """
    Detects anomalies in the sensor data using Isolation Forest.
    
    Args:
        data (list): List of sensor readings.
        contamination (float): The amount of contamination of the data set, i.e. the proportion of outliers in the data set.
        
    Returns:
        list: Indices of the anomalous data points.
    """
    if not data:
        return []
    
    model = IsolationForest(contamination=contamination, random_state=42)
    # Reshape data for sklearn
    data_array = np.array(data).reshape(-1, 1)
    predictions = model.fit_predict(data_array)
    return [i for i, val in enumerate(predictions) if val == -1]

def detect_heat_wave(weather_data, temp_thresh=32, humidity_thresh=60):
    """
    Determines if there is a heat wave risk based on weather data.
    
    Args:
        weather_data (dict): Weather data dictionary from API.
        temp_thresh (float): Temperature threshold for heat wave.
        humidity_thresh (float): Humidity threshold for heat wave.
        
    Returns:
        bool: True if heat wave conditions are met, False otherwise.
    """
    if not weather_data:
        return False
        
    temp = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    # Heat wave conditions
    return temp > temp_thresh and humidity > humidity_thresh
