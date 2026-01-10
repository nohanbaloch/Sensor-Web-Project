import tkinter as tk
from tkinter import messagebox
import requests
import numpy as np
from sklearn.ensemble import IsolationForest
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import io

NASA_API_KEY = 'Jf3gkg0LqSQhjJPyj4tvxy7UIuFyivVPkgxqT6fo'
WEATHER_API_KEY = '3c15aae84bc404fb0d7f71ba9f7be271'


def generate_sensor_data(num_points=100):
    return np.random.normal(25, 5, num_points).tolist()


def fetch_satellite_image(lat, lon):
    url = f"https://api.nasa.gov/planetary/earth/assets"
    params = {
        'lon': lon,
        'lat': lat,
        'dim': 0.1,
        'api_key': NASA_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'url' in data:
            return data['url']
    return None


def fetch_weather_data(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None


def fetch_location_name(lat, lon):
    url = f"http://api.openweathermap.org/geo/1.0/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'limit': 1,
        'appid': WEATHER_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200 and len(response.json()) > 0:
        return response.json()[0].get('name', 'Unknown Location')
    return "Unknown Location"

# using Isolation Forest to detect anomalies 
def detect_anomalies(data):
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(np.array(data).reshape(-1, 1))
    predictions = model.predict(np.array(data).reshape(-1, 1))
    anomalies = [i for i, val in enumerate(predictions) if val == -1]
    return anomalies

# detect wildfire based on weather conditions
def detect_wildfire(weather_data):
    temp = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    
    # Conditions indicating high wildfire risk
    if temp > 35 and humidity < 20 and wind_speed > 5:
        return True
    return False

def plot_data(data, anomalies, wildfire_risk):
    fig, ax = plt.subplots()
    ax.plot(data, label='Sensor Data')
    ax.scatter(anomalies, [data[i] for i in anomalies], color='r', label='Anomalies')
    if wildfire_risk:
        ax.axhline(y=35, color='orange', linestyle='--', label='Wildfire Risk Threshold')
    ax.set_xlabel('Time')
    ax.set_ylabel('Temperature')
    ax.legend()
    ax.grid(True)
    return fig


class SensorWebApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sensor Web Project")
        self.geometry("1000x900") 
        self.configure(bg='#f0f0f0')

        self.sensor_data = generate_sensor_data()
        self.anomalies = []
        self.wildfire_risk = False

        self.create_widgets()

    def create_widgets(self):
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(self.scrollable_frame, text="Enter Latitude:").pack(pady=5)
        self.lat_entry = tk.Entry(self.scrollable_frame)
        self.lat_entry.pack()

        tk.Label(self.scrollable_frame, text="Enter Longitude:").pack(pady=5)
        self.lon_entry = tk.Entry(self.scrollable_frame)
        self.lon_entry.pack()

        self.btn_fetch = tk.Button(self.scrollable_frame, text="Fetch Location & Analyze", command=self.fetch_location_and_analyze)
        self.btn_fetch.pack(pady=20)

        self.weather_label = tk.Label(self.scrollable_frame, text="", wraplength=500)
        self.weather_label.pack(pady=10)

        tk.Label(self.scrollable_frame, text="Temperature Anomalies", font=('Arial', 14)).pack(pady=10)
        self.anomalies_canvas = tk.Canvas(self.scrollable_frame, width=700, height=350)
        self.anomalies_canvas.pack()

       
        self.image_frame = tk.Frame(self, width=500, height=1000, bg="#f0f0f0")
        self.image_frame.pack(side="right", fill="y")

        
        self.image_label = tk.Label(self.image_frame, text="Satellite Image will appear here.")
        self.image_label.pack(pady=10)

        
        self.btn_fetch_image = tk.Button(self.image_frame, text="Fetch Satellite Image", command=self.fetch_image)
        self.btn_fetch_image.pack(pady=20)

    def fetch_location_and_analyze(self):
        try:
            lat = float(self.lat_entry.get())
            lon = float(self.lon_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numerical values for latitude and longitude.")
            return

        location_name = fetch_location_name(lat, lon)
        weather_data = fetch_weather_data(lat, lon)
        
        if weather_data:
            weather_desc = weather_data['weather'][0]['description']
            temp = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            
            self.wildfire_risk = detect_wildfire(weather_data)
            wildfire_status = "High Wildfire Risk!" if self.wildfire_risk else "No Wildfire Risk"
            
            self.weather_label.config(
                text=f"Location: {location_name}\nWeather: {weather_desc.capitalize()}\nTemperature: {temp}°C\nHumidity: {humidity}%\nWind Speed: {wind_speed} m/s\n{wildfire_status}"
            )

        self.anomalies = detect_anomalies(self.sensor_data)
        fig = plot_data(self.sensor_data, self.anomalies, self.wildfire_risk)
        canvas = FigureCanvasTkAgg(fig, master=self.anomalies_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def fetch_image(self):
        try:
            lat = float(self.lat_entry.get())
            lon = float(self.lon_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numerical values for latitude and longitude.")
            return

        image_url = fetch_satellite_image(lat, lon)
        if image_url:
            response = requests.get(image_url)
            if response.status_code == 200:
                image_data = Image.open(io.BytesIO(response.content))
                image_data.thumbnail((500, 400))  
                image = ImageTk.PhotoImage(image_data)
                
                
                self.image_label.configure(image=image)
                self.image_label.image = image  
                self.image_label.pack(pady=20)
            else:
                messagebox.showerror("Error", "Failed to fetch the satellite image.")
        else:
            messagebox.showinfo("No Image", "No satellite image available for the specified location.")


if __name__ == "__main__":
    app = SensorWebApp()
    app.mainloop()