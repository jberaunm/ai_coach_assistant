import React, { useState, useEffect } from "react";

interface AgentFlowDiagramProps {
  websocket: WebSocket | null;
}

interface AgentInteraction {
  id: string;
  agent: string;
  action: string;
  timestamp: Date;
  status: 'active' | 'completed' | 'error';
  details?: string;
}

export default function AgentFlowDiagram({ websocket }: AgentFlowDiagramProps) {
  const [interactions, setInteractions] = useState<AgentInteraction[]>([]);
  const [activeAgents, setActiveAgents] = useState<string[]>([]);

  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle different types of agent interactions
        if (data.type === 'agent_interaction') {
          const newInteraction: AgentInteraction = {
            id: Date.now().toString(),
            agent: data.agent || 'Unknown Agent',
            action: data.action || 'Processing',
            timestamp: new Date(),
            status: data.status || 'active',
            details: data.details
          };

          setInteractions(prev => [newInteraction, ...prev.slice(0, 9)]); // Keep last 10 interactions
          
          // Update active agents
          if (data.status === 'active') {
            setActiveAgents(prev => [...new Set([...prev, data.agent])]);
          } else if (data.status === 'completed' || data.status === 'error') {
            setActiveAgents(prev => prev.filter(agent => agent !== data.agent));
          }
        }
      } catch (error) {
        console.error('Error parsing websocket message:', error);
      }
    };

    websocket.addEventListener('message', handleMessage);
    return () => websocket.removeEventListener('message', handleMessage);
  }, [websocket]);

  // Mock data for demonstration
  useEffect(() => {
    const mockInteractions: AgentInteraction[] = [
      {
        id: '1',
        agent: 'Calendar Agent',
        action: 'Checking availability',
        timestamp: new Date(Date.now() - 5000),
        status: 'completed',
        details: 'Found 3 available slots'
      },
      {
        id: '2',
        agent: 'Weather Agent',
        action: 'Fetching forecast',
        timestamp: new Date(Date.now() - 3000),
        status: 'completed',
        details: 'Sunny, 22°C, perfect for running'
      },
      {
        id: '3',
        agent: 'Training Plan Agent',
        action: 'Analyzing workout',
        timestamp: new Date(Date.now() - 1000),
        status: 'active',
        details: 'Processing 8k easy run recommendation'
      }
    ];

    setInteractions(mockInteractions);
    setActiveAgents(['Training Plan Agent']);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#34A853';
      case 'completed': return '#4285F4';
      case 'error': return '#EA4335';
      default: return '#9AA0A6';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return '⚡';
      case 'completed': return '✓';
      case 'error': return '✗';
      default: return '○';
    }
  };

  return (
    <div className="stat-card agent-flow-card">
      <h3>AI Agent Flow</h3>
      
      {/* Active Agents */}
      <div className="active-agents">
        <h4>Active Agents</h4>
        <div className="agents-grid">
          {activeAgents.length > 0 ? (
            activeAgents.map((agent, index) => (
              <div key={index} className="agent-item active">
                <div className="agent-icon">🤖</div>
                <span className="agent-name">{agent}</span>
                <div className="pulse-indicator"></div>
              </div>
            ))
          ) : (
            <div className="no-active-agents">No active agents</div>
          )}
        </div>
      </div>

      {/* Recent Interactions */}
      <div className="interactions-section">
        <h4>Recent Interactions</h4>
        <div className="interactions-list">
          {interactions.map((interaction) => (
            <div key={interaction.id} className={`interaction-item ${interaction.status}`}>
              <div className="interaction-header">
                <span className="status-icon" style={{ color: getStatusColor(interaction.status) }}>
                  {getStatusIcon(interaction.status)}
                </span>
                <span className="agent-name">{interaction.agent}</span>
                <span className="timestamp">
                  {interaction.timestamp.toLocaleTimeString()}
                </span>
              </div>
              <div className="interaction-action">{interaction.action}</div>
              {interaction.details && (
                <div className="interaction-details">{interaction.details}</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Agent Legend */}
      <div className="agent-legend">
        <div className="legend-item">
          <span className="legend-icon active">⚡</span>
          <span>Active</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon completed">✓</span>
          <span>Completed</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon error">✗</span>
          <span>Error</span>
        </div>
      </div>
    </div>
  );
} 