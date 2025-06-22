"use client";
import React, { useRef, useEffect, useState } from "react";
import Image from "next/image";
import ChatAssistant from "./components/ChatAssistant";
import FileUpload from "./components/FileUpload";

export default function Home() {
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const sessionId = useRef(Math.random().toString().substring(10));
  const [todaysPlan, setTodaysPlan] = useState<string>("Loading...");

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
      <header>
        <h1>AI Coach Running Assistant</h1>
      </header>
      <div className="stats-container">
        <div className="stat-card">
          <h1>Today's plan</h1>
          <h3 className="stat-value" id="todays-plan">{todaysPlan}</h3>
          <h3 className="stat-value">  - 7AM 10 °C</h3>
          <h3 className="stat-value">  - 12PM 22 °C</h3>
        </div>
        <div className="stat-card">
          <h3>Weekly Average</h3>
          <p className="stat-value">45 min</p>
        </div>
      </div>
      <div className="stats-container">
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
        <div className="stat-card">
          <ChatAssistant websocket={websocket} />
        </div>
      </div>
    </>
  );
}
