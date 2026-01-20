import customtkinter as ctk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import io
import requests
from datetime import datetime
import pandas as pd
import tkintermapview

# Import modules
import api_client
import data_processor

class SensorWebApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sensor Web Project")
        self.geometry("1400x900")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Settings variables
        self.heat_wave_temp_thresh = 32
        self.heat_wave_humidity_thresh = 60
        self.anomaly_contamination = 0.1
        self.units = "metric"
        
        # Data state
        self.sensor_data = []
        self.anomalies = []
        self.heat_wave_risk = False
        self.current_weather_data = None
        self.current_location_name = "Unknown"
        self.plot_canvas_widget = None
        self.current_lat_lon = None

        self.create_layout()
        
        # Initial Data
        self.sensor_data = data_processor.generate_sensor_data(base_temp=25)
        self.update_plot()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar (Controls + Map)
        self.left_frame = ctk.CTkFrame(self, width=400, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(3, weight=1) # Map takes expanding space

        # Title
        self.logo_label = ctk.CTkLabel(self.left_frame, text="Sensor Web", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Search
        self.location_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Enter Location")
        self.location_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_fetch = ctk.CTkButton(self.left_frame, text="Search & Analyze", command=self.fetch_location_text)
        self.btn_fetch.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Map Widget
        self.map_widget = tkintermapview.TkinterMapView(self.left_frame, corner_radius=0)
        self.map_widget.grid(row=3, column=0, sticky="nsew", padx=0, pady=0)
        self.map_widget.add_right_click_menu_command(label="Analyze This Location", command=self.on_map_right_click, pass_coords=True)
        self.map_widget.set_position(20, 0) # Default view
        self.map_widget.set_zoom(2)

        # Buttons (Settings, Export)
        self.btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.btn_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        self.btn_settings = ctk.CTkButton(self.btn_frame, text="Settings", command=self.open_settings_window, width=100)
        self.btn_settings.pack(side="left", padx=5, expand=True)
        self.btn_export = ctk.CTkButton(self.btn_frame, text="Export Data", command=self.export_data, width=100)
        self.btn_export.pack(side="right", padx=5, expand=True)


        # Right Main Area (Data & Visuals)
        self.right_frame = ctk.CTkFrame(self, corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_frame.grid_columnconfigure(0, weight=1)
        # self.right_frame.grid_columnconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1) # Charts expand

        # Top Info Bar
        self.info_frame = ctk.CTkFrame(self.right_frame, height=150)
        self.info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.weather_label = ctk.CTkLabel(self.info_frame, text="Welcome! Search a location or right-click on the map.", font=ctk.CTkFont(size=14), justify="left", wraplength=800)
        self.weather_label.pack(side="left", padx=20, pady=20)

        # Charts Area
        self.charts_frame = ctk.CTkFrame(self.right_frame)
        self.charts_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Graph (Left)
        self.graph_frame = ctk.CTkFrame(self.charts_frame)
        self.graph_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Satellite Image (Right)
        self.image_frame = ctk.CTkFrame(self.charts_frame, width=300)
        self.image_frame.pack(side="right", fill="y", padx=5, pady=5)
        
        self.image_label = ctk.CTkLabel(self.image_frame, text="Satellite Image", width=300, height=300)
        self.image_label.pack(pady=20)
        
        self.btn_fetch_image = ctk.CTkButton(self.image_frame, text="Load Satellite Image", command=self.fetch_satellite_image_ui)
        self.btn_fetch_image.pack(pady=10)


    def on_map_right_click(self, coords):
        lat, lon = coords
        print(f"Map clicked: {lat}, {lon}")
        
        # Add marker
        self.map_widget.delete_all_marker()
        self.map_widget.add_marker(lat, lon, text="Selected")
        
        # Fetch name
        name = api_client.fetch_location_name(lat, lon)
        if name:
            self.location_entry.delete(0, "end")
            self.location_entry.insert(0, name)
            self.current_location_name = name
        
        self.perform_analysis(lat, lon, name or f"{lat:.2f}, {lon:.2f}")

    def fetch_location_text(self):
        location_name = self.location_entry.get().strip()
        if not location_name:
            return
        
        lat, lon, full_name = api_client.fetch_coordinates(location_name)
        if lat is None:
            messagebox.showerror("Error", "Location not found")
            return
            
        self.current_location_name = full_name
        self.map_widget.set_position(lat, lon)
        self.map_widget.set_zoom(10)
        self.map_widget.delete_all_marker()
        self.map_widget.add_marker(lat, lon, text=full_name)
        
        self.perform_analysis(lat, lon, full_name)

    def perform_analysis(self, lat, lon, location_name):
        self.current_lat_lon = (lat, lon)
        
        # Fetch Weather
        weather_data = api_client.fetch_weather_data(lat, lon)
        self.current_weather_data = weather_data
        
        temp_val = 25
        if weather_data:
            desc = weather_data['weather'][0]['description']
            temp = weather_data['main']['temp']
            hum = weather_data['main']['humidity']
            wind = weather_data['wind']['speed']
            temp_val = temp
            
            self.heat_wave_risk = data_processor.detect_heat_wave(weather_data, self.heat_wave_temp_thresh, self.heat_wave_humidity_thresh)
            status = "HEAT WAVE WARNING!" if self.heat_wave_risk else "Normal"
            color = "orange" if self.heat_wave_risk else "white"

            self.weather_label.configure(text=f"Location: {location_name}\nCondition: {desc.title()}\nTemp: {temp}°C | Humidity: {hum}% | Wind: {wind} m/s\nStatus: {status}", text_color=color)
        
        # Generate Data
        self.sensor_data = data_processor.generate_sensor_data(base_temp=temp_val)
        self.anomalies = data_processor.detect_anomalies(self.sensor_data, self.anomaly_contamination)
        
        self.update_plot()
        # Reset image label text/image to indicate new location is pending
        self.image_label.configure(image=None, text="Click 'Load Satellite Image' to view.")


    def update_plot(self):
        fig = plt.figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(self.sensor_data, label='Temp Sensor', color='#3B8ED0')
        
        # Anomalies
        if self.anomalies:
             ax.scatter(self.anomalies, [self.sensor_data[i] for i in self.anomalies], color='red', label='Anomaly', zorder=5)
        
        if self.heat_wave_risk:
             ax.axhline(y=self.heat_wave_temp_thresh, color='orange', linestyle='--', label=f'Threshold ({self.heat_wave_temp_thresh}°C)')

        ax.set_title("Real-time Sensor Data Analysis")
        ax.set_xlabel("Time Step")
        ax.set_ylabel("Temperature (°C)")
        ax.legend()
        ax.grid(True, alpha=0.3)

        if self.plot_canvas_widget:
            self.plot_canvas_widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.plot_canvas_widget = canvas.get_tk_widget()
        self.plot_canvas_widget.pack(fill="both", expand=True)
        canvas.draw()
        plt.close(fig)

    def fetch_satellite_image_ui(self):
        if not self.current_lat_lon:
            messagebox.showinfo("Info", "Search for a location first.")
            return
            
        lat, lon = self.current_lat_lon
        url = api_client.fetch_satellite_image(lat, lon)
        if url:
            try:
                resp = requests.get(url)
                img = Image.open(io.BytesIO(resp.content))
                img.thumbnail((300, 300))
                tk_img = ImageTk.PhotoImage(img)
                self.image_label.configure(image=tk_img, text="")
                self.image_label.image = tk_img
            except Exception as e:
                messagebox.showerror("Error", f"Image load failed: {e}")
        else:
             messagebox.showinfo("Info", "No image available.")

    def open_settings_window(self):
        top = ctk.CTkToplevel(self)
        top.title("Settings")
        top.geometry("400x350")
        top.grab_set() # Modal
        
        ctk.CTkLabel(top, text="Heat Wave Temp Threshold (°C):").pack(pady=(20, 5))
        temp_entry = ctk.CTkEntry(top)
        temp_entry.insert(0, str(self.heat_wave_temp_thresh))
        temp_entry.pack()

        ctk.CTkLabel(top, text="Heat Wave Humidity Threshold (%):").pack(pady=5)
        hum_entry = ctk.CTkEntry(top)
        hum_entry.insert(0, str(self.heat_wave_humidity_thresh))
        hum_entry.pack()

        ctk.CTkLabel(top, text="Anomaly Contamination (0.01 - 0.5):").pack(pady=5)
        cont_entry = ctk.CTkEntry(top)
        cont_entry.insert(0, str(self.anomaly_contamination))
        cont_entry.pack()
        
        def save():
            try:
                t = float(temp_entry.get())
                h = float(hum_entry.get())
                c = float(cont_entry.get())
                
                if not (0 < c <= 0.5):
                    raise ValueError("Contamination must be between 0 and 0.5")
                    
                self.heat_wave_temp_thresh = t
                self.heat_wave_humidity_thresh = h
                self.anomaly_contamination = c
                
                messagebox.showinfo("Success", "Settings saved! Re-run analysis to apply.")
                top.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        ctk.CTkButton(top, text="Save Settings", command=save).pack(pady=20)

    def export_data(self):
        if not self.sensor_data:
            messagebox.showinfo("Info", "No data to export.")
            return
            
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            df = pd.DataFrame({
                "Time_Step": range(len(self.sensor_data)),
                "Temperature": self.sensor_data,
                "Is_Anomaly": [1 if i in self.anomalies else 0 for i in range(len(self.sensor_data))]
            })
            
            # Add metadata as comments
            try:
                with open(filename, 'w', newline='') as f:
                    f.write(f"# Location: {self.current_location_name}\n")
                    f.write(f"# Date: {datetime.now()}\n")
                    if self.current_weather_data:
                         desc = self.current_weather_data.get('weather',[{}])[0].get('description','N/A')
                         f.write(f"# Weather: {desc}\n")
                
                df.to_csv(filename, mode='a', index=False)
                messagebox.showinfo("Success", f"Data exported to {filename}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

    def on_closing(self):
        self.quit()
        self.destroy()
