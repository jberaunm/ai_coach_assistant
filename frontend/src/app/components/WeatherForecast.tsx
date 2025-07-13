import React, { useState, useEffect } from "react";
import { useSessionData } from "../contexts/SessionDataContext";

interface WeatherData {
  time: string;
  temperature: string;
  description: string;
  icon: string;
}

interface WeatherForecastProps {
  date: Date;
}

export default function WeatherForecast({ date }: WeatherForecastProps) {
  const { sessionData, loading, error } = useSessionData();
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);

  useEffect(() => {
    if (sessionData?.metadata?.weather?.hours) {
      const hours = sessionData.metadata.weather.hours;
      
      // Convert 24-hour format to 12-hour format and select key hours
      const keyHours = [6, 9, 12, 15, 18]; // 6AM, 9AM, 12PM, 3PM, 6PM
      const selectedWeather = keyHours.map(hour => {
        const hourStr = hour.toString().padStart(2, '0') + ':00';
        const weatherHour = hours.find((h: any) => h.time === hourStr);
        
        if (weatherHour) {
          // Convert 24-hour to 12-hour format
          const displayTime = hour === 0 ? '12AM' : 
                            hour < 12 ? `${hour}AM` : 
                            hour === 12 ? '12PM' : 
                            `${hour - 12}PM`;
          
          // Map weather descriptions to icons
          const getWeatherIcon = (desc: string) => {
            const descLower = desc.toLowerCase();
            if (descLower.includes('sunny')) return '☀️';
            if (descLower.includes('clear')) return '🌙';
            if (descLower.includes('cloudy')) return '☁️';
            if (descLower.includes('partly')) return '⛅';
            if (descLower.includes('rain')) return '🌧️';
            if (descLower.includes('snow')) return '❄️';
            return '🌤️'; // default
          };
          
          return {
            time: displayTime,
            temperature: weatherHour.tempC,
            description: weatherHour.desc,
            icon: getWeatherIcon(weatherHour.desc)
          };
        }
        return null;
      }).filter(Boolean) as WeatherData[];
      
      setWeatherData(selectedWeather);
    } else {
      setWeatherData([]);
    }
  }, [sessionData]);

  return (
    <div className="stat-card weather-forecast-card">
      <div style={{ display: "flex", alignItems: "flex-start", gap: "20px" }}>
        <div 
          style={{ 
            writingMode: "vertical-rl", 
            transform: "rotate(180deg)",
            fontSize: "20px",
            fontWeight: "bold",
            color: "#666",
            padding: "10px 0",
            alignSelf: "center"
          }}
        >
          Weather Forecast
        </div>
        <div style={{ flex: 1 }}>
          <div className="weather-timeline">
            {loading ? (
              <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
                Loading weather data...
              </div>
            ) : weatherData.length > 0 ? (
              weatherData.map((weather, index) => (
                <div key={index} className="weather-slot">
                  <div className="weather-time">{weather.time}</div>
                  <div className="weather-icon">{weather.icon}</div>
                  <div className="weather-temp">{weather.temperature}°C</div>
                  <div className="weather-desc">{weather.description}</div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
                No weather data available
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 