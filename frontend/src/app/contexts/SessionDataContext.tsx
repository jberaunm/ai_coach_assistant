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
    data_points: {
      laps: Array<{
        lap_index: number;
        distance_meters: number;
        pace_ms: number;
        pace_min_km: string;
        heartrate_bpm: number;
        cadence: number;
        elapsed_time: number;
        segment: string;
      }>;
    };
    weather: {
      hours: Array<{
        time: string;
        tempC: string;
        desc: string;
      }>;
    };
    coach_feedback?: string;
  };
}

interface DayStats {
  date: string;
  day_name: string;
  session_type: string;
  planned_distance: number;
  actual_distance: number;
  session_completed: boolean;
  has_activity: boolean;
  is_today: boolean;
  metadata: any;
}

interface WeeklySummary {
  total_distance_planned: number;
  total_distance_completed: number;
  total_sessions: number;
  completed_sessions: number;
  completion_rate: number;
  week_start: string;
  week_end: string;
}

interface WeeklyData {
  status: string;
  data: DayStats[];
  summary: WeeklySummary;
  message: string;
}

interface SessionDataContextType {
  sessionData: SessionData | null;
  weeklyData: WeeklyData | null;
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
  const [weeklyData, setWeeklyData] = useState<WeeklyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scheduling, setScheduling] = useState(false);
  const lastScheduledDate = useRef<string>('');
  const pendingSchedulingDate = useRef<string>('');

  const getMondayOfWeek = (date: Date) => {
    const day = date.getDay();
    const diff = date.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
    return new Date(date.setDate(diff));
  };

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

  const fetchWeeklyData = async () => {
    try {
      const monday = getMondayOfWeek(new Date(date));
      const startDate = monday.toISOString().split('T')[0];
      
      const response = await fetch(`http://localhost:8000/api/weekly/${startDate}`);
      
      if (response.ok) {
        const data: WeeklyData = await response.json();
        setWeeklyData(data);
      } else {
        console.error('Failed to fetch weekly data:', response.status);
        setWeeklyData(null);
      }
    } catch (err) {
      console.error('Error fetching weekly data:', err);
      setWeeklyData(null);
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
        fetchWeeklyData(); // Also refresh weekly data
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
            fetchWeeklyData(); // Also refresh weekly data when agent finishes
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
    
    // Only fetch existing data, don't automatically schedule
    if (formattedDate !== lastScheduledDate.current) {
      lastScheduledDate.current = formattedDate;
      
      // Just fetch existing data without automatic scheduling
      fetchSessionData();
      fetchWeeklyData(); // Also fetch weekly data when date changes
    }
  }, [date, websocket]);

  const refetch = () => {
    fetchSessionData();
    fetchWeeklyData(); // Also refresh weekly data
  };

  const forceSchedule = () => {
    const formattedDate = date.toISOString().split('T')[0];
    scheduleDay(formattedDate);
  };

  return (
    <SessionDataContext.Provider value={{ 
      sessionData, 
      weeklyData,
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