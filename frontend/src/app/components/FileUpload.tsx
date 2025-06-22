"use client";
import React, { useRef, useState } from "react";

interface FileUploadProps {
  websocket: WebSocket | null;
}

export default function FileUpload({ websocket }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<string>("");
  const [dragOver, setDragOver] = useState(false);

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
      <p>{status || "Drag and drop files here or click to upload"}</p>
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
  );
} 