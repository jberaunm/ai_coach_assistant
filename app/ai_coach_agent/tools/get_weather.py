import requests
import xml.etree.ElementTree as ET

def get_weather_forecast() -> list:
    #url = "https://example.com/weather-api?lat=48.85&lon=2.35"
    url= "http://api.worldweatheronline.com/premium/v1/weather.ashx?key=39442c0a352e4a3ba47212917252103&date=today&q=51.59,-0.24&num_of_days=1&tp=1&format=xml"
    response = requests.get(url)

    if response.status_code != 200:
        return [{"status": "error", "message": "Failed to retrieve data."}]

    root = ET.fromstring(response.content)

    # Extract hourly forecasts for the first <weather> entry
    weather = root.find("weather")
    hourly_data = weather.findall("hourly")

    forecast = []
    for hour in hourly_data:
        time = hour.findtext("time")
        temp = hour.findtext("tempC")
        condition = hour.findtext("weatherDesc")
        #icon = hour.findtext("weatherIconUrl")
        #uv = hour.findtext("uvIndex")

        forecast.append({
            "time": f"{int(time)//100:02d}:00",  # Convert "1200" → "12:00"
            "tempC": int(temp),
            "uvIndex": int(uv),
            "desc": condition.strip() if condition else "",
            "icon": icon.strip() if icon else ""
        })

    return forecast