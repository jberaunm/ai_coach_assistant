"use client";
import React, { useRef, useState } from "react";

interface FileUploadProps {
  websocket: WebSocket | null;
}

export default function FileUpload({ websocket }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<string>("");
  const [dragOver, setDragOver] = useState(false);
  const [hasUploadedPlan, setHasUploadedPlan] = useState(false);

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

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <div
        className={`drop-zone${dragOver ? " dragover" : ""}`}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        style={{ cursor: "pointer" }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
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
          <p>{status || "Drag and drop files here or click to upload"}</p>
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
  );
} 