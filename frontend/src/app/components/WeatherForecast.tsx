import React, { useState, useEffect } from "react";

interface WeatherData {
  time: string;
  temperature: number;
  description: string;
  icon: string;
}

interface WeatherForecastProps {
  date: Date;
}

export default function WeatherForecast({ date }: WeatherForecastProps) {
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);

  useEffect(() => {
    // Placeholder weather data - in real app, this would come from a weather API
    setWeatherData([
      { time: "7AM", temperature: 18, description: "Partly Cloudy", icon: "☁️" },
      { time: "10AM", temperature: 22, description: "Sunny", icon: "☀️" },
      { time: "1PM", temperature: 25, description: "Sunny", icon: "☀️" },
      { time: "4PM", temperature: 23, description: "Partly Cloudy", icon: "⛅" },
      { time: "7PM", temperature: 19, description: "Clear", icon: "🌙" },
    ]);
  }, [date]);

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
            {weatherData.map((weather, index) => (
              <div key={index} className="weather-slot">
                <div className="weather-time">{weather.time}</div>
                <div className="weather-icon">{weather.icon}</div>
                <div className="weather-temp">{weather.temperature}°C</div>
                <div className="weather-desc">{weather.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 