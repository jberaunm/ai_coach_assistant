import React, { useState, useEffect } from "react";
import { useSessionData } from "../contexts/SessionDataContext";

interface Event {
  id: number;
  startTime: string;
  endTime: string;
  title: string;
  isAI?: boolean;
}

interface EventsCalendarProps {
  date: Date;
}

export default function EventsCalendar({ date }: EventsCalendarProps) {
  const { sessionData, loading, error } = useSessionData();
  const [events, setEvents] = useState<Event[]>([]);

  useEffect(() => {
    if (sessionData?.metadata?.calendar?.events) {
      const calendarEvents = sessionData.metadata.calendar.events;
      
      // Convert calendar events to the component's Event format
      const formattedEvents = calendarEvents.map((event: any, index: number) => ({
        id: index + 1,
        startTime: event.start,
        endTime: event.end,
        title: event.title || "Untitled Event",
        isAI: event.title ? event.title.endsWith("AI Coach Session") : false // Check if event was created by AI
      }));
      
      setEvents(formattedEvents);
    } else {
      setEvents([]);
    }
  }, [sessionData]);

  return (
    <div className="stat-card events-calendar-card">
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
          Calendar Events
        </div>
        <div style={{ flex: 1 }}>
          <div className="calendar-events">
            {loading ? (
              <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
                Loading calendar events...
              </div>
            ) : events.length > 0 ? (
              events.map((event) => (
                <div key={event.id} className={`event-slot ${event.isAI ? 'ai-event' : ''}`}>
                  <div className="event-time">
                    {event.startTime} - {event.endTime}
                  </div>
                  <div className="event-title">
                    {event.title}
                    {event.isAI && <span className="ai-badge">🤖 AI</span>}
                  </div>
                </div>
              ))
            ) : (
              <div className="event-slot no-events">
                <div className="event-title">No events scheduled</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 