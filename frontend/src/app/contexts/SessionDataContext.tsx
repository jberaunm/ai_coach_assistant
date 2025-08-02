import React, { createContext, useContext, useState, useEffect, ReactNode, useRef } from 'react';

interface SessionData {
  session: string;
  metadata: {
    date: string;
    day: string;
    type: string;
    distance: number;
    notes: string;
    session_completed: boolean;
    time_scheduled: any[];
    calendar: {
      events: Array<{
        title: string;
        start: string;
        end: string;
      }>;
    };
    weather: {
      hours: Array<{
        time: string;
        tempC: string;
        desc: string;
      }>;
    };
  };
}

interface SessionDataContextType {
  sessionData: SessionData | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
  forceSchedule: () => void;
  scheduling: boolean;
}

const SessionDataContext = createContext<SessionDataContextType | undefined>(undefined);

interface SessionDataProviderProps {
  children: ReactNode;
  date: Date;
  websocket?: WebSocket | null;
}

export function SessionDataProvider({ children, date, websocket }: SessionDataProviderProps) {
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scheduling, setScheduling] = useState(false);
  const lastScheduledDate = useRef<string>('');
  const pendingSchedulingDate = useRef<string>('');

  const fetchSessionData = async (specificDate?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Use specificDate if provided (for post-scheduling fetch), otherwise use current date prop
      const formattedDate = specificDate || date.toISOString().split('T')[0];
      const response = await fetch(`http://localhost:8000/api/session/${formattedDate}`);
      
      if (response.ok) {
        const data = await response.json();
        
        // Sort calendar events by start time if they exist
        if (data.metadata?.calendar?.events) {
          data.metadata.calendar.events.sort((a: any, b: any) => {
            // Convert time strings to comparable values (e.g., "06:00" -> 600, "15:30" -> 1530)
            const timeA = parseInt(a.start.replace(':', ''));
            const timeB = parseInt(b.start.replace(':', ''));
            return timeA - timeB; // Ascending order
          });
        }
        
        setSessionData(data);
      } else {
        setError('No session found for this date');
        setSessionData(null);
      }
    } catch (err) {
      console.error('Error fetching session data:', err);
      setError('Failed to load session data');
      setSessionData(null);
    } finally {
      setLoading(false);
    }
  };

  const scheduleDay = async (formattedDate: string) => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not available for scheduling');
      return;
    }

    setScheduling(true);
    pendingSchedulingDate.current = formattedDate;
    
    // Set a fallback timeout in case WebSocket response doesn't come through
    const fallbackTimeout = setTimeout(() => {
      if (pendingSchedulingDate.current === formattedDate) {
        console.warn(`Scheduling timeout for ${formattedDate}, fetching data anyway`);
        fetchSessionData(formattedDate);
        setScheduling(false);
        pendingSchedulingDate.current = '';
      }
    }, 30000); // 30 second fallback timeout
    
    try {
      const message = {
        mime_type: "text/plain",
        data: `Day overview for ${formattedDate}?`,
        role: "user"
      };
      
      websocket.send(JSON.stringify(message));
      console.log(`Day overview request sent for ${formattedDate}`);
      
      // Store the timeout ID to clear it if we get a response
      (scheduleDay as any).fallbackTimeout = fallbackTimeout;
      
    } catch (err) {
      console.error('Error sending Day overview request:', err);
      setScheduling(false);
      pendingSchedulingDate.current = '';
      clearTimeout(fallbackTimeout);
    }
  };

  // Listen for WebSocket messages to detect when scheduling is complete
  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        
        // Check if this is a turn_complete message (agent finished processing)
        if (data.turn_complete === true && pendingSchedulingDate.current) {
          console.log(`Day overview completed for ${pendingSchedulingDate.current}, fetching updated data`);
          
          // Clear the fallback timeout since we got a response
          if ((scheduleDay as any).fallbackTimeout) {
            clearTimeout((scheduleDay as any).fallbackTimeout);
            (scheduleDay as any).fallbackTimeout = null;
          }
          
          // Wait a moment for the database to be updated, then fetch fresh data
          setTimeout(() => {
            fetchSessionData(pendingSchedulingDate.current);
            setScheduling(false);
            pendingSchedulingDate.current = '';
          }, 1000); // Short delay to ensure DB is updated
        }
      } catch (err) {
        // Ignore parsing errors for non-JSON messages
      }
    };

    websocket.addEventListener('message', handleMessage);
    
    return () => {
      websocket.removeEventListener('message', handleMessage);
    };
  }, [websocket]);

  useEffect(() => {
    const formattedDate = date.toISOString().split('T')[0];
    
    // Only schedule if we haven't scheduled this date before
    if (formattedDate !== lastScheduledDate.current) {
      lastScheduledDate.current = formattedDate;
      
      // First try to fetch existing data
      fetchSessionData().then(() => {
        // If no data exists or data is incomplete, schedule the day
        if (!sessionData || !sessionData.metadata?.weather?.hours?.length || !sessionData.metadata?.calendar?.events?.length) {
          scheduleDay(formattedDate);
        }
      });
    }
  }, [date, websocket]);

  const refetch = () => {
    fetchSessionData();
  };

  const forceSchedule = () => {
    const formattedDate = date.toISOString().split('T')[0];
    scheduleDay(formattedDate);
  };

  return (
    <SessionDataContext.Provider value={{ 
      sessionData, 
      loading: loading || scheduling, 
      error, 
      refetch, 
      forceSchedule,
      scheduling 
    }}>
      {children}
    </SessionDataContext.Provider>
  );
}

export function useSessionData() {
  const context = useContext(SessionDataContext);
  if (context === undefined) {
    throw new Error('useSessionData must be used within a SessionDataProvider');
  }
  return context;
} 