import React, { useState, useEffect } from "react";

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
  const [events, setEvents] = useState<Event[]>([]);

  useEffect(() => {
    // Placeholder fetch logic for events
    setEvents([
      { id: 1, startTime: "10:00", endTime: "10:30", title: "Meeting A", isAI: false },
      { id: 2, startTime: "12:00", endTime: "13:30", title: "Meeting B", isAI: false },
      { id: 3, startTime: "14:00", endTime: "14:30", title: "Running Session", isAI: true },
      { id: 4, startTime: "15:00", endTime: "15:30", title: "Meeting D", isAI: false },
    ]);
  }, [date]);

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
            {events.length > 0 ? (
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