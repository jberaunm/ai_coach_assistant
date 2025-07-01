import React, { useState, useEffect } from "react";

interface WeeklyStatsProps {
  date: Date;
}

interface DayStats {
  date: Date;
  sessionType: string;
  distance: number;
  isToday: boolean;
}

export default function WeeklyStats({ date }: WeeklyStatsProps) {
  const [weekStats, setWeekStats] = useState<DayStats[]>([]);
  const [totalDistance, setTotalDistance] = useState(0);
  const [totalSessions, setTotalSessions] = useState(0);

  useEffect(() => {
    // Get the Monday of the current week
    const getMondayOfWeek = (date: Date) => {
      const day = date.getDay();
      const diff = date.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
      return new Date(date.setDate(diff));
    };

    const monday = getMondayOfWeek(new Date(date));
    const weekDays: DayStats[] = [];

    // Sample session types
    const sessionTypes = ["Easy Run", "Tempo Run", "Long Run", "Recovery", "Rest Day", "Speed Work", "Hill Training"];

    // Generate stats for each day of the week (Monday to Sunday)
    for (let i = 0; i < 7; i++) {
      const currentDate = new Date(monday);
      currentDate.setDate(monday.getDate() + i);
      
      // Mock data - replace with actual API call
      const mockDistance = Math.floor(Math.random() * 15) + 1; // 1-15 km
      const mockSessionType = sessionTypes[Math.floor(Math.random() * sessionTypes.length)];
      
      weekDays.push({
        date: currentDate,
        sessionType: mockSessionType,
        distance: mockDistance,
        isToday: currentDate.toDateString() === new Date().toDateString()
      });
    }

    setWeekStats(weekDays);
    
    // Calculate total distance
    const totalDist = weekDays.reduce((sum, day) => sum + day.distance, 0);
    setTotalDistance(totalDist);
    
    // Calculate total sessions (excluding rest days)
    const totalSess = weekDays.filter(day => day.sessionType !== "Rest Day").length;
    setTotalSessions(totalSess);
  }, [date]);

  const formatDayName = (date: Date) => {
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  };

  const formatDate = (date: Date) => {
    return date.getDate().toString();
  };

  return (
    <div className="stat-card weekly-stats-card">
      <h1>Weekly Overview</h1>
      
      {/* Daily breakdown */}
      <div className="weekly-breakdown">
        <div className="days-grid">
          {weekStats.map((day, index) => (
            <div 
              key={index} 
              className={`day-item ${day.isToday ? 'today' : ''} ${day.distance > 0 ? 'has-activity' : 'no-activity'}`}
            >
              <div className="day-header">
                <span className="day-name">{formatDayName(day.date)}</span>
                <span className="day-date">{formatDate(day.date)}</span>
              </div>
              <div className="day-stats">
                <div className="stat-item">
                  <span className="stat-value session-type">{day.sessionType}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{day.distance} km</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Weekly totals */}
      <div className="weekly-totals">
        <div className="total-item">
          <span className="total-label">Total Distance</span>
          <span className="total-value">{totalDistance} km</span>
        </div>
        <div className="total-item">
          <span className="total-label">Total Sessions</span>
          <span className="total-value">{totalSessions}</span>
        </div>
      </div>

    </div>
  );
} 