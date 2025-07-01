import React, { useState, useEffect } from "react";

interface DayOverviewCardProps {
  date: Date;
  onDateChange: (date: Date) => void;
}

export default function DayOverviewCard({ date, onDateChange }: DayOverviewCardProps) {
  const [plan, setPlan] = useState("Loading...");
  const [weather, setWeather] = useState("Loading...");
  const [scheduledTime, setScheduledTime] = useState("Loading...");

  useEffect(() => {
    // Placeholder fetch logic for plan
    setPlan(`Plan for ${date.toDateString()}`);
    // Placeholder fetch logic for weather
    setWeather(`Weather for ${date.toDateString()}`);
    // Placeholder fetch logic for scheduled time
    setScheduledTime(`08:00 AM`);
  }, [date]);

  const goToNextDay = () => {
    const next = new Date(date);
    next.setDate(date.getDate() + 1);
    onDateChange(next);
  };

  const goToPrevDay = () => {
    const prevDay = new Date(date);
    prevDay.setDate(date.getDate() - 1);
    onDateChange(prevDay);
  };

  return (
    <div style={{ 
      backgroundColor: "#fff",
      borderRadius: "12px",
      padding: "20px 20px",
      textAlign: "center",
      height: "fit-content",
      width: "100%"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <button onClick={goToPrevDay}>{'<'}</button>
        <h1>{date.toDateString()}</h1>
        <button onClick={goToNextDay}>{'>'}</button>
      </div>
      {/*<h3 className="stat-value">Plan: {plan}</h3>*/}
      <div style={{ 
        display: "flex", 
        justifyContent: "space-between", 
        alignItems: "center",
        width: "100%",
        marginTop: "20px"
      }}>
        {/* Column 1: Session Type */}
        <div style={{ 
          display: "flex", 
          flexDirection: "column", 
          alignItems: "center",
          flex: 1
        }}>
          <div style={{ 
            fontSize: "46px", 
            fontWeight: "600", 
            color: "var(--primary-color)",
            lineHeight: "1.2"
          }}>
            Easy
          </div>
          <div style={{ 
            fontSize: "34px", 
            fontWeight: "500", 
            color: "var(--primary-color)",
            lineHeight: "1.2"
          }}>
            Run
          </div>
        </div>

        {/* Column 2: Distance */}
        <div style={{ 
          display: "flex", 
          alignItems: "center",
          justifyContent: "center",
          flex: 1
        }}>
          <div style={{ 
            fontSize: "90px", 
            fontWeight: "600", 
            color: "var(--primary-color)",
            lineHeight: "1.2"
          }}>
            <span style={{ fontWeight: "600" }}>8</span>
            <span style={{ fontWeight: "300", fontSize: "60px" }}>k</span>
          </div>
        </div>

        {/* Column 3: Description */}
        <div style={{ 
          display: "flex", 
          alignItems: "center",
          justifyContent: "center",
          flex: 1
        }}>
          <div style={{ 
            width: "100px",
            textAlign: "center",
            fontSize: "22px",
            fontWeight: "500",
            color: "var(--primary-color)",
            lineHeight: "1.3"
          }}>
            Finish with strides
          </div>
        </div>
      </div>
    </div>
  );
} 