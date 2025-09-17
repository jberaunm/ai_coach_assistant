import React, { useEffect, useState, useCallback, useRef } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  Position,
  NodeTypes,
  Handle
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { Node as RFNode } from 'reactflow';

// Custom RootNode component with multiple handles
const RootNode: React.FC<{ data: { label: string } }> = ({ data }) => {
  return (
    <div style={{ 
      background: '#cc785c', 
      color: '#fff', 
      borderRadius: 8, 
      padding: 8, 
      fontWeight: 600, 
      fontSize: 24, 
      width: 230,
      position: 'relative'
    }}>
      <Handle
        type="source"
        position={Position.Top}
        id="root-top"
        style={{ background: '#fff', border: '2px solid #4e9cea' }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="root-right"
        style={{ background: '#fff', border: '2px solid #4e9cea' }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="root-bottom"
        style={{ background: '#fff', border: '2px solid #4e9cea' }}
      />
      <Handle
        type="target"
        position={Position.Left}
        id="root-left"
        style={{ background: '#fff', border: '2px solid #4e9cea' }}
      />
      {data.label}
    </div>
  );
};

// Custom WeatherToolNode component with icon
const WeatherToolNode: React.FC<{ data: { label: string; icon?: string } }> = ({ data }) => {
  return (
    <div style={{ 
      background: 'transparent', 
      color: '#fff', 
      borderRadius: 8, 
      padding: 8, 
      fontWeight: 400, 
      fontSize: 24, 
      width: 250,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative'
    }}>
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        style={{ background: '#fff', border: '2px solid #4e9cea' }}
      />
      {data.icon ? (
        <img 
          src={data.icon} 
          alt="Weather API" 
          style={{ 
            width: 250, 
            height: 90, 
            objectFit: 'contain',
            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))'
          }} 
        />
      ) : (
        <div style={{
          background: '#a020f0', 
          color: '#fff', 
          borderRadius: 8, 
          padding: 8, 
          fontWeight: 400, 
          fontSize: 24, 
          width: '100%',
          textAlign: 'center'
        }}>
          {data.label}
        </div>
      )}
    </div>
  );
};

// Custom CalendarToolNode component with icon
const CalendarToolNode: React.FC<{ data: { label: string; icon?: string } }> = ({ data }) => {
  return (
    <div style={{ 
      background: 'transparent', 
      color: '#fff', 
      borderRadius: 8, 
      padding: 8, 
      fontWeight: 400, 
      fontSize: 24, 
      width: 240,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative'
    }}>
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        style={{ background: '#fff', border: '2px solid #4e9cea' }}
      />
      {data.icon ? (
        <img 
          src={data.icon} 
          alt="Calendar API" 
          style={{ 
            width: 240, 
            height: 90, 
            objectFit: 'contain',
            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))'
          }} 
        />
      ) : (
        <div style={{
          background: '#a020f0', 
          color: '#fff', 
          borderRadius: 2, 
          padding: 2, 
          fontWeight: 400, 
          fontSize: 24, 
          width: '100%',
          textAlign: 'center'
        }}>
          {data.label}
        </div>
      )}
    </div>
  );
};

// Custom StravaToolNode component with icon
const StravaToolNode: React.FC<{ data: { label: string; icon?: string } }> = ({ data }) => {
  return (
    <div style={{ 
      background: 'transparent', 
      color: '#fff', 
      borderRadius: 8, 
      padding: 8, 
      fontWeight: 400, 
      fontSize: 24, 
      width: 230,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative'
    }}>
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        style={{ background: '#fff', border: '2px solid #4e9cea' }}
      />
      {data.icon ? (
        <img 
          src={data.icon} 
          alt="Strava API" 
          style={{ 
            width: 230, 
            height: 70, 
            objectFit: 'contain',
            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))'
          }} 
        />
      ) : (
        <div style={{
          background: '#a020f0', 
          color: '#fff', 
          borderRadius: 2, 
          padding: 2, 
          fontWeight: 400, 
          fontSize: 24, 
          width: '100%',
          textAlign: 'center'
        }}>
          {data.label}
        </div>
      )}
    </div>
  );
};

// Define custom node types
const nodeTypes: NodeTypes = {
  rootNode: RootNode,
  weatherToolNode: WeatherToolNode,
  calendarToolNode: CalendarToolNode,
  stravaToolNode: StravaToolNode,
};

  const initialNodes: Node[] = [
    { 
      id: 'root', 
      position: { x: -100, y: 190 }, 
      data: { label: 'Coach Agent\nGemini-Flash-exp' }, 
      type: 'rootNode', // Use custom node type
      style: { background: '#cc785c', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 24, width: 240 }
      // Remove sourcePosition and targetPosition as they're now handled by custom handles
    },
    { 
      id: 'planner', 
      position: { x: 150, y: -30 }, 
      data: { label: 'Planner Agent\nMistral-Small' }, 
      style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 23, width: 230 }, 
      sourcePosition: Position.Right, 
      targetPosition: Position.Left 
    },
    { 
      id: 'scheduler', 
      position: { x: 210, y: 80 }, 
      data: { label: 'Scheduler Agent\nMistral-Small' }, 
      style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 23, width: 240 }, 
      sourcePosition: Position.Right, 
      targetPosition: Position.Left 
    },
    { 
      id: 'strava', 
      position: { x: 240, y: 190 }, 
      data: { label: 'Strava Agent\nMistral-Small' }, 
      style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 23, width: 230 }, 
      sourcePosition: Position.Right, 
      targetPosition: Position.Left 
    },
    { 
      id: 'analyser', 
      position: { x: 210, y: 300 }, 
      data: { label: 'Analyser Agent\nMistral-Small' }, 
      style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 23, width: 250 },
      sourcePosition: Position.Right, 
      targetPosition: Position.Left 
    },
    {
      id: 'rag_agent', 
      position: { x: 150, y: 410 }, 
      data: { label: 'RAG Agent\nGemini-2.5-pro' }, 
      style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 23, width: 220 }, 
      sourcePosition: Position.Right, 
      targetPosition: Position.Left  
    },
    { 
      id: 'tool_file_reader', 
      position: { x: 450, y: -60 }, 
      data: { label: 'FileReader tool' }, 
      style: { background: '#a020f0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 400, fontSize: 24, width: 220 }, 
      sourcePosition: Position.Right, 
      targetPosition: Position.Left 
    },
    { 
      id: 'tool_weatherapi', 
      position: { x: 510, y: 30 }, 
      data: { label: 'WeatherAPI tool', icon: '/weather-api.png' }, 
      type: 'weatherToolNode',
      style: { background: 'transparent', color: '#fff', borderRadius: 0, padding: 0, fontWeight: 400, fontSize: 0, width: 250 }, 
      targetPosition: Position.Left 
    },
     { 
       id: 'tool_calendarapi', 
       position: { x: 530, y: 140 }, 
       data: { label: 'CalendarAPI', icon: '/calendar_api.png' }, 
       type: 'calendarToolNode',
       style: { background: 'transparent', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 400, fontSize: 24, width: 250 }, 
       targetPosition: Position.Left 
     },
    { 
      id: 'tool_stravaapi', 
      position: { x: 520, y: 260 }, 
      data: { label: 'StravaAPI tool', icon: '/strava_api.png' }, 
      type: 'stravaToolNode',
      style: { background: 'transparent', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 400, fontSize: 24, width: 250 }, 
      targetPosition: Position.Left 
    },
    { 
      id: 'rag_db', 
      position: { x: 500, y: 390 }, 
      data: { label: 'Retrieval-Augmented (RAG) Knowledge base' }, 
      style: { background: '#a020f0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 400, fontSize: 24, width: 280 }, 
      targetPosition: Position.Left 
    }
  ];

  const initialEdges: Edge[] = [
    { 
      id: 'e1', 
      source: 'root', 
      target: 'planner', 
      sourceHandle: 'root-top', // Use the top handle from custom root node
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#1565c0', strokeWidth: 4 } 
    },
    { 
      id: 'e2', 
      source: 'root', 
      target: 'scheduler', 
      sourceHandle: 'root-right', // Use the right handle from custom root node
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#1565c0', strokeWidth: 4 } 
    },
    { 
      id: 'e3', 
      source: 'root', 
      target: 'strava', 
      sourceHandle: 'root-right', // Use the right handle from custom root node
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#1565c0', strokeWidth: 4 } 
    },
    { 
      id: 'e4', 
      source: 'root', 
      target: 'analyser', 
      sourceHandle: 'root-right', // Use the right handle from custom root node
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#1565c0', strokeWidth: 4 } 
    },
    { 
      id: 'e5', 
      source: 'root', 
      target: 'rag_agent', 
      sourceHandle: 'root-bottom', // Use the right handle from custom root node
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#1565c0', strokeWidth: 4 } 
    },
    { 
      id: 'e6', 
      source: 'planner', 
      target: 'tool_file_reader', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e7', 
      source: 'scheduler', 
      target: 'tool_weatherapi', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e8', 
      source: 'scheduler', 
      target: 'tool_calendarapi', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e9', 
      source: 'scheduler', 
      target: 'tool_calendarapi_create', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e10', 
      source: 'strava', 
      target: 'tool_stravaapi', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e11', 
      source: 'analyser', 
      target: 'rag_db', 
      sourceHandle: 'root-right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e12', 
      source: 'rag_agent', 
      target: 'rag_db', 
      sourceHandle: 'bottom', 
      targetHandle: 'top',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e13', 
      source: 'planner', 
      target: 'rag_db', 
      sourceHandle: 'bottom', 
      targetHandle: 'top',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    }
  ];

interface AgentFlowDiagramReactFlowProps {
  websocket?: WebSocket | null;
}

interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  type: 'agent_start' | 'agent_finish' | 'tool_start' | 'tool_finish' | 'error' | 'info';
  component: string;
}

export default function AgentFlowDiagramReactFlow({ websocket }: AgentFlowDiagramReactFlowProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [activeEdge, setActiveEdge] = useState<string | null>(null);
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const [lastLogTime, setLastLogTime] = useState<number>(0);
  const logTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Track active agents and tools (items that have started but not finished)
  const [activeAgents, setActiveAgents] = useState<Set<string>>(new Set());
  const [activeTools, setActiveTools] = useState<Set<string>>(new Set());
  
  // Log viewer state
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [overallStatus, setOverallStatus] = useState<'idle' | 'active' | 'error'>('idle');
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Function to add log entry
  const addLog = useCallback((message: string, type: LogEntry['type'], component: string) => {
    const logEntry: LogEntry = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toLocaleTimeString(),
      message,
      type,
      component
    };
    
    setLogs(prev => {
      const newLogs = [...prev, logEntry];
      // Keep only last 50 logs to prevent memory issues
      return newLogs.slice(-50);
    });

    // Update overall status based on log type
    if (type === 'agent_start' || type === 'tool_start') {
      setOverallStatus('active');
    } else if (type === 'error') {
      setOverallStatus('error');
    } else if (type === 'agent_finish' || type === 'tool_finish') {
      // Check if there are any active agents or tools
      setOverallStatus(prev => {
        // This will be updated by the actual agent/tool state changes
        return prev;
      });
    }
  }, []);

  // Auto-scroll to bottom of logs (only within the log container)
  useEffect(() => {
    if (logsEndRef.current) {
      const logContainer = logsEndRef.current.parentElement;
      if (logContainer) {
        logContainer.scrollTop = logContainer.scrollHeight;
      }
    }
  }, [logs]);

  // Update overall status based on active agents and tools
  useEffect(() => {
    if (activeAgents.size > 0 || activeTools.size > 0) {
      setOverallStatus('active');
    } else {
      setOverallStatus('idle');
    }
  }, [activeAgents, activeTools]);

  // Status icon function for overall status
  const getOverallStatusIcon = () => {
    switch (overallStatus) {
      case 'active':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="animate-spin">
            <circle cx="12" cy="12" r="10" stroke="#3b82f6" strokeWidth="2" fill="none" strokeDasharray="31.416" strokeDashoffset="31.416">
              <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
              <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
            </circle>
          </svg>
        );
      case 'error':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ color: "#ef4444" }}>
            <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        );
      case 'idle':
      default:
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ color: "#10b981" }}>
            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        );
    }
  };


  // Function to highlight nodes based on log pattern
  const highlightNodesFromLog = useCallback((logMessage: string) => {
    console.log('Processing log message:', logMessage);
    
    // Add log entry for all messages
    addLog(logMessage, 'info', 'System');
    
    // Individual cases for each agent START/FINISH events
    if (logMessage.includes('[PLANNER_AGENT] START:')) {
      addLog('Planner Agent started', 'agent_start', 'Planner Agent');
      handleAgentStart('planner', 'Planner Agent', ['e1','e13']);
    } else if (logMessage.includes('[PLANNER_AGENT] FINISH:')) {
      addLog('Planner Agent finished', 'agent_finish', 'Planner Agent');
      handleAgentFinish('planner', 'Planner Agent');
    } else if (logMessage.includes('[SCHEDULER_AGENT] START:')) {
      addLog('Scheduler Agent started', 'agent_start', 'Scheduler Agent');
      handleAgentStart('scheduler', 'Scheduler Agent', ['e2']);
    } else if (logMessage.includes('[SCHEDULER_AGENT] FINISH:')) {
      addLog('Scheduler Agent finished', 'agent_finish', 'Scheduler Agent');
      handleAgentFinish('scheduler', 'Scheduler Agent');
    } else if (logMessage.includes('[STRAVA_AGENT] START:')) {
      addLog('Strava Agent started', 'agent_start', 'Strava Agent');
      handleAgentStart('strava', 'Strava Agent', ['e3']);
    } else if (logMessage.includes('[STRAVA_AGENT] FINISH:')) {
      addLog('Strava Agent finished', 'agent_finish', 'Strava Agent');
      handleAgentFinish('strava', 'Strava Agent');
    } else if (logMessage.includes('[ANALYSER_AGENT] START:')) {
      addLog('Analyser Agent started', 'agent_start', 'Analyser Agent');
      handleAgentStart('analyser', 'Analyser Agent', ['e4','e11']);
    } else if (logMessage.includes('[ANALYSER_AGENT] FINISH:')) {
      addLog('Analyser Agent finished', 'agent_finish', 'Analyser Agent');
      handleAgentFinish('analyser', 'Analyser Agent');
    } else if (logMessage.includes('[RAG_AGENT] START:')) {
      addLog('RAG Agent started', 'agent_start', 'RAG Agent');
      handleAgentStart('rag_agent', 'RAG Agent', ['e5','e12']);
    } else if (logMessage.includes('[RAG_AGENT] FINISH:')) {
      addLog('RAG Agent finished', 'agent_finish', 'RAG Agent');
      handleAgentFinish('rag_agent', 'RAG Agent');
    }
    
    // Individual cases for each tool START events with duration
    else if (logMessage.includes('[FileReader_tool] START:')) {
      addLog('File Reader Tool started', 'tool_start', 'File Reader Tool');
      handleToolStart('tool_file_reader', 'File Reader Tool', 10, ['e6']);
    } else if (logMessage.includes('[CalendarAPI_tool] START:')) {
      addLog('Calendar API Tool started', 'tool_start', 'Calendar API Tool');
      handleToolStart('tool_calendarapi', 'Calendar API Tool', 10, ['e8']);
    } else if (logMessage.includes('[WeatherAPI_tool] START:')) {
      addLog('Weather API Tool started', 'tool_start', 'Weather API Tool');
      handleToolStart('tool_weatherapi', 'Weather API Tool', 10, ['e7']);
    } else if (logMessage.includes('[StravaAPI_tool] START:')) {
      addLog('Strava API Tool started', 'tool_start', 'Strava API Tool');
      handleToolStart('tool_stravaapi', 'Strava API Tool', 10, ['e10']);
    } else if (logMessage.includes('[RAG_knowledge_base] START:')) {
      addLog('RAG Knowledge Base accessed', 'tool_start', 'RAG Knowledge Base');
      handleToolStart('rag_db', 'RAG Knowledge Base', 10);
    }
    
  }, [setNodes, setEdges, addLog]);

  // Helper function to handle agent start
  const handleAgentStart = useCallback((agentId: string, displayName: string, edgeIds: string[] = []) => {
    console.log(`Agent START: ${displayName}`);
    setActiveAgents(prev => new Set(prev).add(agentId));
    
    // Highlight the agent node and root node with animation
    setNodes(nds => nds.map(n => ({
      ...n,
      style: {
        ...n.style,
        boxShadow: (n.id === agentId || n.id === 'root') ? '0 0 16px 4px #68da81' : n.style?.boxShadow,
        zIndex: (n.id === agentId || n.id === 'root') ? 10 : n.style?.zIndex || 1,
      },
    })));
    
    // Animate specified edges
    setEdges(eds => eds.map(e => {
      const shouldAnimate = edgeIds.includes(e.id);
      return {
        ...e,
        animated: shouldAnimate,
        style: {
          ...e.style,
          stroke: shouldAnimate ? '#EA4335' : (e.style?.stroke || '#1976d2'),
          strokeWidth: shouldAnimate ? 4 : 2,
        },
      };
    }));
    
    setActiveNode(displayName);
    setLastLogTime(Date.now());

    // Auto-finish agent after 30 seconds if no finish message is received
    setTimeout(() => {
      // Check if agent is still active (no finish message received)
      setActiveAgents(prev => {
        if (prev.has(agentId)) {
          console.log(`Auto-finishing agent: ${displayName} after 30s timeout`);
          // Remove from active agents
          const newSet = new Set(prev);
          newSet.delete(agentId);
          
          // Remove highlighting from the agent node and root node
          setNodes(nds => nds.map(n => ({
            ...n,
            style: {
              ...n.style,
              boxShadow: (n.id === agentId || n.id === 'root') ? undefined : n.style?.boxShadow,
              zIndex: (n.id === agentId || n.id === 'root') ? 1 : n.style?.zIndex || 1,
            },
          })));
          
          // Stop animating ALL edges when an agent finishes
          setEdges(eds => eds.map(e => ({
            ...e,
            animated: false,
            style: {
              ...e.style,
              stroke: e.style?.stroke || '#1976d2',
              strokeWidth: 2,
            },
          })));
          
          // Clear all tool highlighting when an agent finishes
          setNodes(nds => nds.map(n => ({
            ...n,
            style: {
              ...n.style,
              boxShadow: (n.id.includes('api') || n.id === 'file_reader' || n.id === 'rag_db') ? undefined : n.style?.boxShadow,
              zIndex: (n.id.includes('api') || n.id === 'file_reader' || n.id === 'rag_db') ? 1 : n.style?.zIndex || 1,
            },
          })));
          
          setActiveNode(null);
          return newSet;
        }
        return prev;
      });
    }, 30000);
  }, [setNodes, setEdges]);

  // Helper function to handle agent finish
  const handleAgentFinish = useCallback((agentId: string, displayName: string) => {
    console.log(`Agent FINISH: ${displayName}`);
    setActiveAgents(prev => {
      const newSet = new Set(prev);
      newSet.delete(agentId);
      return newSet;
    });
    
    // Remove highlighting from the agent node and root node
    setNodes(nds => nds.map(n => ({
      ...n,
      style: {
        ...n.style,
        boxShadow: (n.id === agentId || n.id === 'root') ? undefined : n.style?.boxShadow,
        zIndex: (n.id === agentId || n.id === 'root') ? 1 : n.style?.zIndex || 1,
      },
    })));
    
    // Stop animating ALL edges when an agent finishes
    setEdges(eds => eds.map(e => ({
      ...e,
      animated: false,
      style: {
        ...e.style,
        stroke: e.style?.stroke || '#1976d2',
        strokeWidth: 2,
      },
    })));
    
    // Clear all tool highlighting when an agent finishes
    setNodes(nds => nds.map(n => ({
      ...n,
      style: {
        ...n.style,
        boxShadow: (n.id.includes('api') || n.id === 'file_reader' || n.id === 'rag_db') ? undefined : n.style?.boxShadow,
        zIndex: (n.id.includes('api') || n.id === 'file_reader' || n.id === 'rag_db') ? 1 : n.style?.zIndex || 1,
      },
    })));
    
    setActiveNode(null);
  }, [setNodes, setEdges]);

  // Helper function to handle tool start with duration
  const handleToolStart = useCallback((toolId: string, displayName: string, durationSeconds: number = 2, edgeIds: string[] = []) => {
    console.log(`Tool START: ${displayName} (${durationSeconds}s)`);
    setActiveTools(prev => new Set(prev).add(toolId));
    
    // Highlight the tool node
    setNodes(nds => nds.map(n => ({
      ...n,
      style: {
        ...n.style,
        boxShadow: n.id === toolId ? '0 0 16px 4px #68da81' : n.style?.boxShadow,
        zIndex: n.id === toolId ? 10 : n.style?.zIndex || 1,
      },
    })));

    // Animate specified edges
    setEdges(eds => eds.map(e => {
      const shouldAnimate = edgeIds.includes(e.id);
      return {
        ...e,
        animated: shouldAnimate,
        style: {
          ...e.style,
          stroke: shouldAnimate ? '#EA4335' : e.style?.stroke,
          strokeWidth: shouldAnimate ? 4 : e.style?.strokeWidth || 2,
        },
      };
    }));

    setActiveNode(displayName);
    setLastLogTime(Date.now());

    // Auto-remove highlighting after specified duration
    setTimeout(() => {
      setActiveTools(prev => {
        const newSet = new Set(prev);
        newSet.delete(toolId);
        return newSet;
      });
      
      // Remove highlighting from the tool node
      setNodes(nds => nds.map(n => ({
        ...n,
        style: {
          ...n.style,
          boxShadow: n.id === toolId ? undefined : n.style?.boxShadow,
          zIndex: n.id === toolId ? 1 : n.style?.zIndex || 1,
        },
      })));

      // Stop animating specified edges and reset their style
      setEdges(eds => eds.map(e => {
        const shouldStopAnimation = edgeIds.includes(e.id);
        return {
          ...e,
          animated: shouldStopAnimation ? false : e.animated,
          style: {
            ...e.style,
            stroke: shouldStopAnimation ? (e.style?.stroke || '#1976d2') : e.style?.stroke,
            strokeWidth: shouldStopAnimation ? 2 : e.style?.strokeWidth,
          },
        };
      }));

      setActiveNode(null);
    }, durationSeconds * 1000);
  }, [setNodes, setEdges]);


  // Helper function to highlight a specific node
  const highlightSpecificNode = useCallback((nodeId: string, displayName: string) => {
    // Highlight the node
    setNodes(nds => nds.map(n => ({
      ...n,
      style: {
        ...n.style,
        boxShadow: n.id === nodeId ? '0 0 16px 4px #68da81' : n.style?.boxShadow,
        zIndex: n.id === nodeId ? 10 : n.style?.zIndex || 1,
      },
    })));

    // Highlight connecting edges
    setEdges(eds => eds.map(e => ({
      ...e,
      animated: e.source === nodeId || e.target === nodeId,
      style: {
        ...e.style,
        stroke: (e.source === nodeId || e.target === nodeId) ? '#EA4335' : e.style?.stroke,
        strokeWidth: (e.source === nodeId || e.target === nodeId) ? 4 : e.style?.strokeWidth || 2,
      },
    })));

    // Set active node for display
    setActiveNode(displayName);
    setLastLogTime(Date.now());
  }, [setNodes, setEdges]);

  // Listen to WebSocket messages for log data
  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        
        // Check if this is a log message from the backend
        if (data.log_message) {
          console.log('Processing log message from backend:', data.log_message);
          highlightNodesFromLog(data.log_message);
        }
        
        // Check for agent responses that might contain log information
        if (data.mime_type === 'text/plain' && data.data) {
          const message = data.data;
          
          // Look for specific log patterns in the agent response
          const logPatterns = [
            '[FRONTEND TO AGENT]',
            '[PLANNER_AGENT]',
            '[SCHEDULER_AGENT]',
            '[STRAVA_AGENT]',
            '[ANALYSER_AGENT]',
            '[RAG_AGENT]',
            '[FileReader_tool]',
            '[CalendarAPI_tool]',
            '[WeatherAPI_tool]',
            '[StravaAPI_tool]',
            'START:',
            'FINISH:'
          ];
          
          for (const pattern of logPatterns) {
            if (message.includes(pattern)) {
              highlightNodesFromLog(pattern);
              break;
            }
          }
        }
      } catch (error) {
        // Ignore parsing errors for non-JSON messages
      }
    };

    websocket.addEventListener('message', handleMessage);

    return () => {
      websocket.removeEventListener('message', handleMessage);
    };
  }, [websocket, highlightNodesFromLog]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (logTimeoutRef.current) {
        clearTimeout(logTimeoutRef.current);
      }
    };
  }, []);

  // Node click handler for interactivity
  const onNodeClick = useCallback((event: React.MouseEvent, node: RFNode) => {
    alert(`Clicked on ${node.data.label}`);
  }, []);

  // Get WebSocket connection status
  const getConnectionStatus = () => {
    if (!websocket) return { status: 'disconnected', color: '#ef4444', text: 'Disconnected' };
    switch (websocket.readyState) {
      case WebSocket.CONNECTING:
        return { status: 'connecting', color: '#f59e0b', text: 'Connecting...' };
      case WebSocket.OPEN:
        return { status: 'connected', color: '#10b981', text: 'Connected' };
      case WebSocket.CLOSING:
        return { status: 'closing', color: '#f59e0b', text: 'Closing...' };
      case WebSocket.CLOSED:
        return { status: 'disconnected', color: '#ef4444', text: 'Disconnected' };
      default:
        return { status: 'unknown', color: '#6b7280', text: 'Unknown' };
    }
  };

  const connectionStatus = getConnectionStatus();

  return (
    <div className="stat-card agent-flow-card" style={{ width: 440, height: 420, padding: '2px 0 2px 0', paddingLeft: 0, display: 'flex', flexDirection: 'column' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        panOnDrag={false}
        zoomOnScroll={false}
        zoomOnPinch={false}
        zoomOnDoubleClick={false}
        nodeTypes={nodeTypes}
        style={{ height: 250, flex: 1 }}
      >
        {/* <MiniMap /> and <Controls /> Removed for cleaner look */}
        <Background />
      </ReactFlow>
      
      {/* Log Viewer Component */}
      <div style={{ 
        borderTop: '1px solid #e2e8f0', 
        padding: '8px 12px', 
        backgroundColor: '#f8fafc',
        height: '100px',
        flexShrink: 0
      }}>
        {/* Log Viewer Header with Single Status */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '8px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: connectionStatus.color
            }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#374151' }}>
              Agent Logs ({logs.length})
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {getOverallStatusIcon()}
            <span style={{ 
              fontSize: '11px', 
              color: overallStatus === 'active' ? '#3b82f6' : overallStatus === 'error' ? '#ef4444' : '#10b981',
              fontWeight: '500'
            }}>
              {overallStatus === 'active' ? 'Active' : overallStatus === 'error' ? 'Error' : 'Idle'}
            </span>
          </div>
        </div>

        {/* Log Entries */}
        <div style={{ 
          height: '60px', 
          overflowY: 'auto', 
          backgroundColor: '#ffffff',
          borderRadius: '6px',
          border: '1px solid #e2e8f0',
          padding: '6px'
        }}>
          {logs.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              color: '#9ca3af', 
              fontSize: '12px',
              padding: '20px 0'
            }}>
              No logs yet. Agent activity will appear here.
            </div>
          ) : (
            logs.map((log) => (
              <div key={log.id} style={{ 
                display: 'flex', 
                alignItems: 'flex-start', 
                gap: '8px', 
                padding: '4px 0',
                borderBottom: '1px solid #f1f5f9'
              }}>
                <div style={{ 
                  fontSize: '10px', 
                  color: '#9ca3af',
                  minWidth: '40px',
                  marginTop: '2px'
                }}>
                  {log.timestamp}
                </div>
                <div style={{ flex: 1, fontSize: '11px', lineHeight: '1.4' }}>
                  <div style={{ 
                    fontWeight: '500', 
                    color: '#374151',
                    marginBottom: '2px'
                  }}>
                    {log.component}
                  </div>
                  <div style={{ 
                    color: '#6b7280',
                    wordBreak: 'break-word'
                  }}>
                    {log.message}
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  );
} 