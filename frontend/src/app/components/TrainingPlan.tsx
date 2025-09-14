"use client";
import React, { useRef, useState } from "react";
import { useSessionData } from "../contexts/SessionDataContext";

interface TrainingPlanProps {
  websocket: WebSocket | null;
}

export default function TrainingPlan({ websocket }: TrainingPlanProps) {
  const { sendMessage } = useSessionData();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<string>("");
  const [dragOver, setDragOver] = useState(false);
  const [hasUploadedPlan, setHasUploadedPlan] = useState(false);
  
  // Form state for personalized plan
  const [goalPlan, setGoalPlan] = useState<string>("");
  const [raceDate, setRaceDate] = useState<string>("");
  const [age, setAge] = useState<string>("");
  const [weight, setWeight] = useState<string>("");
  const [avgKmsPerWeek, setAvgKmsPerWeek] = useState<string>("");
  const [fastest5kTime, setFastest5kTime] = useState<string>("");

  const goalPlanOptions = [
    "General Fitness",
    "5k",
    "10k", 
    "Half-marathon",
    "Marathon",
    "Ultra-Marathon",
  ];

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFiles = (files: FileList) => {
    if (!websocket) return;
    const file = files[0];
    if (!file) return;
    setStatus("Uploading...");
    const formData = new FormData();
    formData.append("file", file);
    // Get session ID from websocket URL
    let sessionId = "";
    try {
      const wsUrl = new URL(websocket.url);
      sessionId = wsUrl.pathname.split("/").pop() || "";
    } catch {}
    const uploadUrl = `http://localhost:8000/upload?session_id=${sessionId}`;
    // console.log("WebSocket URL used for upload:", websocket?.url);
    fetch(uploadUrl, { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setStatus("File uploaded successfully!");
          setHasUploadedPlan(true);
        } else {
          setStatus("Upload failed. Please try again.");
        }
      })
      .catch(() => setStatus("Upload failed. Please try again."))
      .finally(() => {
        setTimeout(() => setStatus(""), 3000);
      });
  };

  const handleCreatePersonalizedPlan = () => {
    if (!sendMessage) {
      console.error("sendMessage function not available");
      setStatus("Error: Unable to send message");
      return;
    }

    if (!goalPlan) {
      setStatus("Please select a goal plan");
      setTimeout(() => setStatus(""), 3000);
      return;
    }

    // Create the request message for planner_agent Workflow 2
    const requestMessage = `Create personalized training plan with:
    Goal Plan: ${goalPlan}
    ${raceDate ? `Race Date: ${raceDate}` : ''}
    ${age ? `Age: ${age}` : ''}
    ${weight ? `Weight: ${weight} kg` : ''}
    ${avgKmsPerWeek ? `Average KMs per Week: ${avgKmsPerWeek}` : ''}
    ${fastest5kTime ? `5K Fastest Time: ${fastest5kTime}` : ''}`;

    console.log("Creating personalized plan with:", {
      goalPlan,
      raceDate,
      age,
      weight,
      avgKmsPerWeek,
      fastest5kTime
    });

    // Send the message via WebSocket
    const success = sendMessage(requestMessage);
    
    if (success) {
      setStatus("Creating your personalized training plan...");
      console.log("Personalized plan request sent successfully");
    } else {
      setStatus("Failed to send request. Please try again.");
    }

    // Clear status after 5 seconds
    setTimeout(() => setStatus(""), 5000);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
      {/* Top Row - File Upload */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <h2 style={{ 
          margin: "0 0 16px 0", 
          fontSize: "20px", 
          fontWeight: "600",
          color: "#1e293b"
        }}>
          Upload Training Plan
        </h2>
        
        <div
          className={`drop-zone${dragOver ? " dragover" : ""}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          style={{ 
            cursor: "pointer",
            border: "2px dashed #d1d5db",
            borderRadius: "8px",
            padding: "32px",
            textAlign: "center",
            backgroundColor: dragOver ? "#f3f4f6" : "#fafafa",
            transition: "all 0.2s ease"
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "12px" }}>
            {hasUploadedPlan ? (
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                style={{ color: "#10b981" }}
              >
                <path
                  d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            ) : (
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                style={{ color: "#6b7280" }}
              >
                <path
                  d="M12 5V19M5 12H19"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
            <p style={{ margin: 0, color: "#6b7280" }}>
              {status || "Drag and drop files here or click to upload"}
            </p>
          </div>
          <input
            type="file"
            id="fileUpload"
            ref={fileInputRef}
            hidden
            onChange={(e) => {
              if (e.target.files) handleFiles(e.target.files);
            }}
          />
        </div>
        
        {hasUploadedPlan && (
          <div style={{
            padding: "16px",
            backgroundColor: "#f8fafc",
            borderRadius: "8px",
            border: "1px solid #e2e8f0"
          }}>
            <h3 style={{ 
              margin: "0 0 8px 0", 
              fontSize: "16px", 
              fontWeight: "600",
              color: "#1e293b"
            }}>
              Training Plan Summary
            </h3>
            <div style={{ display: "flex", gap: "24px", fontSize: "14px" }}>
              <div>
                <span style={{ color: "#64748b" }}>Total Weeks: </span>
                <span style={{ fontWeight: "600", color: "#1e293b" }}>
                  12
                </span>
              </div>
              <div>
                <span style={{ color: "#64748b" }}>Total Workouts: </span>
                <span style={{ fontWeight: "600", color: "#1e293b" }}>
                  48
                </span>
              </div>
              <div>
                <span style={{ color: "#64748b" }}>File: </span>
                <span style={{ fontWeight: "600", color: "#1e293b" }}>
                  training_plan.csv
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Row - Personalized Plan Form */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <h2 style={{ 
          margin: "0 0 16px 0", 
          fontSize: "20px", 
          fontWeight: "600",
          color: "#1e293b"
        }}>
          Create Personalized Plan
        </h2>
        
        <div style={{
          padding: "24px",
          backgroundColor: "#f8fafc",
          borderRadius: "8px",
          border: "1px solid #e2e8f0"
        }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* First Row: Goal Plan and Race Date */}
            <div style={{ display: "flex", gap: "16px" }}>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  Goal Plan *
                </label>
                <select
                  value={goalPlan}
                  onChange={(e) => setGoalPlan(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px",
                    backgroundColor: "white"
                  }}
                >
                  <option value="">Select your goal</option>
                  {goalPlanOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  Race Date
                </label>
                <input
                  type="date"
                  value={raceDate}
                  onChange={(e) => setRaceDate(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
              </div>
            </div>

            {/* Second Row: Age, Weight, and Average KMs */}
            <div style={{ display: "flex", gap: "16px" }}>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  Age
                </label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="25"
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  Weight (kg)
                </label>
                <input
                  type="number"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                  placeholder="70"
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  Average KMs per Week
                </label>
                <input
                  type="number"
                  value={avgKmsPerWeek}
                  onChange={(e) => setAvgKmsPerWeek(e.target.value)}
                  placeholder="20"
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
              </div>
            </div>

            {/* Third Row: 5K Time and Create Button */}
            <div style={{ display: "flex", gap: "16px", alignItems: "end" }}>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  5K Fastest Time (mm:ss)
                </label>
                <input
                  type="text"
                  value={fastest5kTime}
                  onChange={(e) => setFastest5kTime(e.target.value)}
                  placeholder="25:30"
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
              </div>
              <div style={{ flex: 1 }}>
                <button
                  onClick={handleCreatePersonalizedPlan}
                  disabled={!goalPlan}
                  style={{
                    width: "100%",
                    padding: "12px 24px",
                    backgroundColor: goalPlan ? "#3b82f6" : "#9ca3af",
                    color: "white",
                    border: "none",
                    borderRadius: "6px",
                    fontSize: "14px",
                    fontWeight: "500",
                    cursor: goalPlan ? "pointer" : "not-allowed",
                    transition: "background-color 0.2s ease"
                  }}
                >
                  Create Personalized Plan
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
