"use client";
import React, { useRef, useEffect, useState } from "react";
import Image from "next/image";
import ChatAssistant from "./components/ChatAssistant";
import FileUpload from "./components/FileUpload";
import DayOverviewCard from "./components/DayOverviewCard";
import EventsCalendar from "./components/EventsCalendar";
import WeatherForecast from "./components/WeatherForecast";
import WeeklyStats from "./components/WeeklyStats";
import SessionOverview from "./components/SessionOverview";
import AgentFlowDiagramReactFlow from "./components/AgentFlowDiagramReactFlow";
import { SessionDataProvider } from "./contexts/SessionDataContext";

export default function Home() {
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const sessionId = useRef(Math.random().toString().substring(10));
  const [todaysPlan, setTodaysPlan] = useState<string>("Loading...");
  const [sharedDate, setSharedDate] = useState(new Date());

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId.current}?is_audio=false`);
    setWebsocket(ws);
    return () => ws.close();
  }, []);

  useEffect(() => {
    fetch("http://localhost:8000/api/todays-session")
      .then((res) => {
        if (!res.ok) throw new Error("No session found for today");
        return res.json();
      })
      .then((data) => {
        if (data.metadata) {
          const type = data.metadata.type || "No type";
          // Only show distance if it exists and is not 0
          const distance = (data.metadata.distance && Number(data.metadata.distance) !== 0)
            ? ` - ${data.metadata.distance}`
            : "";
          setTodaysPlan(`${type}${distance}`);
        } else {
          setTodaysPlan("No plan found");
        }
      })
      .catch(() => setTodaysPlan("No plan found"));
  }, []);

  return (
    <>
      <header style={{ display: "flex", justifyContent: "space-between", padding: "2px 14px", alignItems: "center" }}>
        <Image 
          src="/runningAI_logo.png" 
          alt="Running AI Logo" 
          width={120} 
          height={25} 
          priority
        />
        <nav style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <button 
            style={{ 
              background: "none", 
              border: "none", 
              cursor: "pointer", 
              padding: "8px",
              borderRadius: "8px",
              transition: "background-color 0.2s ease"
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f0f0f0"}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
            title="Notifications"
          >
            <Image 
              src="/notification.png" 
              alt="Notifications" 
              width={20} 
              height={20} 
            />
          </button>
          <button 
            style={{ 
              background: "none", 
              border: "none", 
              cursor: "pointer", 
              padding: "8px",
              borderRadius: "8px",
              transition: "background-color 0.2s ease"
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f0f0f0"}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
            title="Settings"
          >
            <Image 
              src="/settings.png" 
              alt="Settings" 
              width={20} 
              height={20} 
            />
          </button>
          <button 
            style={{ 
              background: "none", 
              border: "none", 
              cursor: "pointer", 
              padding: "8px",
              borderRadius: "8px",
              transition: "background-color 0.2s ease"
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f0f0f0"}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
            title="User Profile"
          >
            <Image 
              src="/profile.png" 
              alt="User Profile" 
              width={20} 
              height={20} 
            />
          </button>
        </nav>
      </header>
      <div className="dashboard-layout">
        <SessionDataProvider date={sharedDate} websocket={websocket}>
          <div className="main-stats-container">
            <DayOverviewCard date={sharedDate} onDateChange={setSharedDate} />
            <WeatherForecast date={sharedDate} />
            <EventsCalendar date={sharedDate} />
          </div>
          <div className="side-containers">
            <WeeklyStats date={sharedDate} />
            {/* SessionOverview: Shows compact session info, opens detailed popup on click */}
            <SessionOverview date={sharedDate} />
            <div className="stat-card">
              <h1>Training plan</h1>
              <FileUpload websocket={websocket} />
              <div id="training-plan-status" style={{display: "none", alignItems: "center", gap: "8px"}}>
                <svg id="uploaded-icon" width="24" height="24" fill="none" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="12" fill="#34A853" />
                  <path d="M7 13l3 3 7-7" stroke="#fff" strokeWidth="2" fill="none" />
                </svg>
                <span>Training plan uploaded and processed</span>
              </div>
            </div>
          </div>
        </SessionDataProvider>
        <div className="third-column">
          <div className="stat-card">
            <h1 style={{ marginBottom: 12 }}>Chat Interaction</h1>
            <ChatAssistant websocket={websocket} />
          </div>
          <div className="stat-card agent-flow-card">
            <h1 style={{ marginBottom: 12 }}>AI Agent Flow</h1>
            <AgentFlowDiagramReactFlow websocket={websocket} />
          </div>
        </div>
      </div>
    </>
  );
}
