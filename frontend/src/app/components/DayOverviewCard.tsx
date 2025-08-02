import React, { useState, useEffect } from "react";
import { useSessionData } from "../contexts/SessionDataContext";

interface DayOverviewCardProps {
  date: Date;
  onDateChange: (date: Date) => void;
}

export default function DayOverviewCard({ date, onDateChange }: DayOverviewCardProps) {
  const { sessionData, loading, error, forceSchedule, scheduling } = useSessionData();
  
  // Extract data from shared context
  const sessionType = sessionData?.metadata?.type || "No Session";
  const distance = sessionData?.metadata?.distance?.toString() || "0";
  const notes = sessionData?.metadata?.notes || "No additional notes";
  const sessionCompleted = sessionData?.metadata?.session_completed || false;

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
      backgroundColor: sessionCompleted ? "#e8f5e8" : "#fff",
      borderRadius: "12px",
      padding: "20px 20px",
      textAlign: "center",
      height: "fit-content",
      width: "100%",
      border: sessionCompleted ? "2px solid #4caf50" : "1px solid #e0e0e0",
      transition: "all 0.3s ease"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <button onClick={goToPrevDay}>{'<'}</button>
        <div style={{ textAlign: "center" }}>
          <h1>{date.toDateString()}</h1>
          {sessionCompleted && (
            <div style={{ 
              fontSize: "12px", 
              color: "#4caf50", 
              marginTop: "4px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "4px",
              fontWeight: "600"
            }}>
              <span>✓</span>
              Completed
            </div>
          )}
          {scheduling && !sessionCompleted && (
            <div style={{ 
              fontSize: "12px", 
              color: "#666", 
              marginTop: "4px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "4px"
            }}>
              <div style={{ 
                width: "8px", 
                height: "8px", 
                borderRadius: "50%", 
                backgroundColor: "#007bff",
                animation: "pulse-dot 1.5s infinite"
              }}></div>
              Scheduling...
            </div>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <button 
            onClick={forceSchedule}
            disabled={scheduling}
            style={{
              padding: "4px 8px",
              fontSize: "12px",
              backgroundColor: scheduling ? "#ccc" : "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: scheduling ? "not-allowed" : "pointer"
            }}
            title="Refresh schedule data"
          >
            🔄
          </button>
          <button onClick={goToNextDay}>{'>'}</button>
        </div>
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
          {loading ? (
            <div style={{ 
              fontSize: "42px", 
              fontWeight: "600", 
              color: "var(--primary-color)",
              lineHeight: "1.2"
            }}>
              Loading...
            </div>
          ) : (
            <>
              <div style={{ 
                fontSize: "38px", 
                fontWeight: "600", 
                color: "var(--primary-color)",
                lineHeight: "1.2"
              }}>
                {sessionType === "Loading..." || sessionType === "No Session" ? "No" : 
                 sessionType.includes(" ") ? sessionType.split(" ")[0] : sessionType}
              </div>
              <div style={{ 
                fontSize: "34px", 
                fontWeight: "500", 
                color: "var(--primary-color)",
                lineHeight: "1.2"
              }}>
                {sessionType === "Loading..." || sessionType === "No Session" ? "Session" : 
                 sessionType.includes(" ") ? sessionType.split(" ").slice(1).join(" ") : ""}
              </div>
            </>
          )}
        </div>

        {/* Column 2: Distance */}
        <div style={{ 
          display: "flex", 
          alignItems: "center",
          justifyContent: "center",
          flex: 1
        }}>
          <div style={{ 
            fontSize: "70px", 
            fontWeight: "600", 
            color: "var(--primary-color)",
            lineHeight: "1.2"
          }}>
            {loading ? (
              <span>...</span>
            ) : (
              <>
                <span style={{ fontWeight: "600" }}>{distance}</span>
                <span style={{ fontWeight: "300", fontSize: "50px" }}>k</span>
              </>
            )}
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
            fontSize: "18px",
            fontWeight: "500",
            color: "var(--primary-color)",
            lineHeight: "1.3"
          }}>
            {loading ? "Loading..." : notes}
          </div>
        </div>
      </div>
    </div>
  );
} 