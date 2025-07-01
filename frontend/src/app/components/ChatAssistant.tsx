"use client";
import React, { useEffect, useRef, useState } from "react";

interface Message {
  id: string;
  text: string;
  role: "user" | "model";
  isAudio?: boolean;
}

interface ChatAssistantProps {
  websocket: WebSocket | null;
}

export default function ChatAssistant({ websocket }: ChatAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const [typing, setTyping] = useState(false);
  const [currentMessageId, setCurrentMessageId] = useState<string | null>(null);
  const messagesDivRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!websocket) return;
    const ws = websocket;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (event) => {
      const message_from_server = JSON.parse(event.data);
      // Typing indicator
      if (
        !message_from_server.turn_complete &&
        (message_from_server.mime_type === "text/plain" ||
          message_from_server.mime_type === "audio/pcm")
      ) {
        setTyping(true);
      }
      if (message_from_server.turn_complete === true) {
        setCurrentMessageId(null);
        setTyping(false);
        return;
      }
      if (message_from_server.mime_type === "text/plain") {
        setTyping(false);
        const role = message_from_server.role || "model";
        // If we already have a message element for this turn, append to it
        if (currentMessageId && role === "model") {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === currentMessageId
                ? { ...msg, text: msg.text + message_from_server.data }
                : msg
            )
          );
          scrollToBottom();
          return;
        }
        // New message
        const messageId = Math.random().toString(36).substring(7);
        setMessages((prev) => [
          ...prev,
          {
            id: messageId,
            text: message_from_server.data,
            role,
          },
        ]);
        if (role === "model") setCurrentMessageId(messageId);
        scrollToBottom();
      }
    };
    return () => {
      ws.onopen = null;
      ws.onclose = null;
      ws.onerror = null;
      ws.onmessage = null;
    };
  }, [websocket, currentMessageId]);

  // Scroll to bottom
  const scrollToBottom = () => {
    setTimeout(() => {
      if (messagesDivRef.current) {
        messagesDivRef.current.scrollTop = messagesDivRef.current.scrollHeight;
      }
    }, 0);
  };

  // Handle form submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !websocket || websocket.readyState !== 1) return;
    const userMsg: Message = {
      id: Math.random().toString(36).substring(7),
      text: input,
      role: "user",
    };
    setMessages((prev) => [...prev, userMsg]);
    websocket.send(
      JSON.stringify({ mime_type: "text/plain", data: input, role: "user" })
    );
    setInput("");
    setTyping(true);
    scrollToBottom();
  };

  return (
    <div className="chat-container">
      <div id="messages" ref={messagesDivRef} style={{ height: 200, overflowY: "auto", padding: 20, background: "white", display: "flex", flexDirection: "column" }}>
        {messages.map((msg) => (
          <p
            key={msg.id}
            className={msg.role === "user" ? "user-message" : "agent-message"}
          >
            {msg.text}
          </p>
        ))}
        <div
          id="typing-indicator"
          className={"typing-indicator" + (typing ? " visible" : "")}
        >
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
      <form id="messageForm" onSubmit={handleSubmit} style={{ display: "flex", gap: 10, padding: 16, background: "white", borderTop: "1px solid #f8f9fa" }}>
        <input
          type="text"
          id="message"
          name="message"
          placeholder="Type your message here..."
          autoComplete="off"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ flex: 1, padding: "12px 16px", border: "1px solid #dadce0", borderRadius: 24, fontSize: 16 }}
        />
        <button type="submit" id="sendButton" disabled={!connected || !input.trim()}>
          Send
        </button>
      </form>
      <div className="status-indicator">
        <div className="status-item">
          <div id="status-dot" className={"status-dot" + (connected ? " connected" : "")}></div>
          <span id="connection-status">{connected ? "Connected" : "Disconnected. Reconnecting..."}</span>
        </div>
      </div>
    </div>
  );
} 