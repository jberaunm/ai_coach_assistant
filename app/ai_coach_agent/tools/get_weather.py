import requests
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_weather_forecast(date: Optional[str] = None) -> Dict:
    """
    Get weather forecast for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format. If None, uses today's date.
        
    Returns:
        Dict containing weather forecast data with current conditions and hourly forecast
    """
    # Get API key from environment variable or use fallback
    api_key = os.getenv("WORLDWEATHER_API_KEY")

    # Hardcoded coordinates for London
    lat = "51.59"
    lon = "-0.24"
    
    # Use today's date if none provided
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Build URL with parameters
    url = f"http://api.worldweatheronline.com/premium/v1/weather.ashx"
    params = {
        "key": api_key,
        "date": date,
        "q": f"{lat},{lon}",
        "num_of_days": "1",
        "tp": "1",  # 1-hour intervals
        "format": "xml"
    }
    
    try:
        print(f"[WeatherAPI_tool]")
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return {
                "status": "error", 
                "message": f"Failed to retrieve data. Status code: {response.status_code}"
            }
        
        root = ET.fromstring(response.content)
        
        # Get current conditions
        current_condition = root.find("current_condition")
        current_data = {}
        if current_condition is not None:
            current_data = {
                "observation_time": current_condition.findtext("observation_time"),
                "tempC": current_condition.findtext("temp_C"),
                "weatherDesc": current_condition.findtext("weatherDesc"),
            }
        
        # Get hourly forecasts
        weather = root.find("weather")
        if weather is None:
            return {
                "status": "error",
                "message": "No weather data found in response"
            }
        
        hourly_data = weather.findall("hourly")
        
        # Get current time to filter future hours
        current_time = datetime.now()
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        # If target date is today, filter by current hour
        if target_date.date() == current_time.date():
            current_hour = current_time.hour
        else:
            # If target date is in the future, include all hours
            current_hour = -1
        
        forecast_hours = []
        for hour in hourly_data:
            time_str = hour.findtext("time")
            if time_str is None:
                continue
                
            # Convert time format (e.g., "2200" to hour 22)
            try:
                hour_int = int(time_str) // 100
            except ValueError:
                continue
            
            # Only include future hours
            if hour_int > current_hour:
                temp = hour.findtext("tempC")
                condition = hour.findtext("weatherDesc")
                
                forecast_hours.append({
                    "time": f"{hour_int:02d}:00",
                    "tempC": temp,
                    "desc": condition.strip() if condition else "",
                })
        
        return {
            "status": "success",
            "date": date,
            "current_condition": current_data,
            "weather": {
                "hours": forecast_hours
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error retrieving weather data: {str(e)}"
        }