# Sensor Web Project

A Python-based desktop application that integrates satellite imagery, weather data, and machine learning to monitor environmental conditions and detect potential hazards like wildfires.

## Features

- **Real-time Weather Data**: Fetches current weather conditions (temperature, humidity, wind speed) for any given latitude and longitude using the OpenWeatherMap API.
- **Satellite Imagery**: Retrieves recent satellite images from NASA's Earth assets for specified locations.
- **Anomaly Detection**: Uses the **Isolation Forest** machine learning algorithm to identify anomalies in temperature sensor data.
- **Wildfire Risk Assessment**: Analyzes weather patterns to calculate and alert on high wildfire risks.
- **Data Visualization**: Interactive plotting of sensor data and detected anomalies using Matplotlib.
- **User-Friendly GUI**: Built with Tkinter, featuring a scrollable interface for easy navigation.

## Technologies Used

- **Python 3.x**
- **Tkinter**: GUI framework
- **Scikit-Learn**: Machine learning (Isolation Forest)
- **Matplotlib**: Data visualization
- **Requests**: API communication
- **Pillow (PIL)**: Image processing
- **NumPy**: Numerical operations

## Getting Started

### Prerequisites

You will need API keys from:

1. [NASA API](https://api.nasa.gov/)
2. [OpenWeatherMap API](https://openweathermap.org/api)

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Sensor_Web_Project
   ```

2. Install the required dependencies:

   ```bash
   pip install requests numpy scikit-learn matplotlib pillow
   ```

3. Run the application:
   ```bash
   python Sensor_Web_Project_tkinter.py
   ```

## Usage

1. Enter the **Latitude** and **Longitude** of the location you wish to monitor.
2. Click **Fetch Location & Analyze** to get the latest weather report and run the anomaly detection algorithm.
3. Click **Fetch Satellite Image** to view the environmental layout of the area.
4. Review the visualization to see temperature trends and any identified data anomalies.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
