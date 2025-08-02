import React, { useState, useEffect } from "react";

interface WeeklyStatsProps {
  date: Date;
}

interface DayStats {
  date: string;
  day_name: string;
  sessionType: string;
  distance: number;
  session_completed: boolean;
  has_activity: boolean;
  is_today: boolean;
  metadata: any;
}

interface WeeklySummary {
  total_distance: number;
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

export default function WeeklyStats({ date }: WeeklyStatsProps) {
  const [weekStats, setWeekStats] = useState<DayStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Calculate totals from the weekStats data
  const calculateTotals = () => {
    if (!weekStats.length) return { completedDistance: 0, plannedDistance: 0, totalSessions: 0, completedSessions: 0, completionRate: 0 };
    
    let completedDistance = 0;
    let plannedDistance = 0;
    let totalSessions = 0;
    let completedSessions = 0;
    
    console.log('Calculating totals for weekStats:', weekStats);
    
    weekStats.forEach(day => {
      console.log(`Day ${day.date}: has_activity=${day.has_activity}, session_completed=${day.session_completed}, distance=${day.distance}`);
      
      if (day.has_activity) {
        totalSessions++;
        plannedDistance += day.distance;
        
        if (day.session_completed) {
          completedSessions++;
          completedDistance += day.distance;
          console.log(`  -> Completed session found: ${day.date}`);
        }
      }
    });
    
    console.log(`Final totals: completedSessions=${completedSessions}, totalSessions=${totalSessions}`);
    
    const completionRate = totalSessions > 0 ? (completedSessions / totalSessions) * 100 : 0;
    
    return {
      completedDistance,
      plannedDistance,
      totalSessions,
      completedSessions,
      completionRate
    };
  };
  
  const totals = calculateTotals();

  useEffect(() => {
    const fetchWeeklyData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Get the Monday of the current week
        const getMondayOfWeek = (date: Date) => {
          const day = date.getDay();
          const diff = date.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
          return new Date(date.setDate(diff));
        };

        const monday = getMondayOfWeek(new Date(date));
        const startDate = monday.toISOString().split('T')[0];
        
        const response = await fetch(`http://localhost:8000/api/weekly/${startDate}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const weeklyData: WeeklyData = await response.json();
        
        if (weeklyData.status === "success") {
          setWeekStats(weeklyData.data);
        } else {
          // If it's an error, show it, but also set empty data
          setError(weeklyData.message || "Failed to load weekly data");
          setWeekStats([]);
        }
      } catch (err) {
        console.error('Error fetching weekly data:', err);
        setError('Failed to load weekly data');
      } finally {
        setLoading(false);
      }
    };

    fetchWeeklyData();
  }, [date]);

  const formatDayName = (dayName: string) => {
    return dayName.substring(0, 3); // Get first 3 characters (Mon, Tue, etc.)
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).getDate().toString();
  };

  if (loading) {
    return (
      <div className="stat-card weekly-stats-card">
        <h1>Weekly Overview</h1>
        <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
          Loading weekly data...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stat-card weekly-stats-card">
        <h1>Weekly Overview</h1>
        <div style={{ textAlign: "center", padding: "20px", color: "#f44336" }}>
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="stat-card weekly-stats-card">
      <h1>Weekly Overview</h1>
      
      {/* Daily breakdown */}
      <div className="weekly-breakdown">
        <div className="days-grid">
          {weekStats.map((day, index) => {
            // Determine CSS classes for the day item
            const dayClasses = ['day-item'];
            
            if (day.is_today) {
              dayClasses.push('today');
              if (day.session_completed) {
                dayClasses.push('completed');
              } else {
                dayClasses.push('incomplete');
              }
            }
            
            if (day.has_activity) {
              dayClasses.push('has-activity');
            } else {
              dayClasses.push('no-activity');
            }
            
            return (
            <div 
              key={index} 
              className={dayClasses.join(' ')}
            >
              <div className="day-header">
                <span className="day-name">{formatDayName(day.day_name)}</span>
                <span className="day-date">{formatDate(day.date)}</span>
              </div>
              <div className="day-stats">
                <div className="stat-item">
                  <span className="stat-value session-type">{day.sessionType}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{day.distance}k</span>
                </div>
              </div>
            </div>
          );
          })}
        </div>
      </div>

      {/* Weekly totals */}
      <div className="weekly-totals">
        <div className="total-item">
          <span className="total-label">Distance</span>
          <span className="total-value">{totals.completedDistance}/{totals.plannedDistance}k</span>
        </div>
        <div className="total-item">
          <span className="total-label">Total Sessions</span>
          <span className="total-value">{totals.totalSessions}</span>
        </div>
        <div className="total-item">
          <span className="total-label">Completed</span>
          <span className="total-value">{totals.completedSessions}</span>
        </div>
        <div className="total-item">
          <span className="total-label">Completion Rate</span>
          <span className="total-value">{totals.completionRate.toFixed(0)}%</span>
        </div>
      </div>

    </div>
  );
} 