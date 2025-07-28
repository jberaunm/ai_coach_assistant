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
      width: 260,
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

// Define custom node types
const nodeTypes: NodeTypes = {
  rootNode: RootNode,
};

  const initialNodes: Node[] = [
    { 
      id: 'root', 
      position: { x: -100, y: 190 }, 
      data: { label: 'Root Agent\nLLM: Gemini-Flash-exp' }, 
      type: 'rootNode', // Use custom node type
      style: { background: '#cc785c', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 24, width: 270 }
      // Remove sourcePosition and targetPosition as they're now handled by custom handles
    },
    { 
      id: 'planner', 
      position: { x: 150, y: -30 }, 
      data: { label: 'Planner Agent\nLLM: Mistral-Small' }, 
      style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 23, width: 230 }, 
      sourcePosition: Position.Right, 
      targetPosition: Position.Left 
    },
    { 
      id: 'scheduler', 
      position: { x: 230, y: 80 }, 
      data: { label: 'Scheduler Agent\nLLM: Mistral-Small' }, 
      style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 23, width: 240 }, 
      sourcePosition: Position.Right, 
      targetPosition: Position.Left 
    },
    { 
      id: 'strava', 
      position: { x: 250, y: 190 }, 
      data: { label: 'Strava Agent\nLLM: MistralAI' }, 
      style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 23, width: 210 }, 
      sourcePosition: Position.Right, 
      targetPosition: Position.Left 
    },
    { 
      id: 'analyser', 
      position: { x: 230, y: 300 }, 
      data: { label: 'Analyser Squential\nAgent' }, 
      style: { background: '#4e9cea', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 23, width: 220 },
      targetPosition: Position.Left 
    },
    {
      id: 'num_analyser', 
      position: { x: 10, y: 430 }, 
      data: { label: 'Num Analyser Agent\nLLM: Mistral-Small' }, 
      style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 22, width: 240 }, 
      sourcePosition: Position.Right 
    },
    { 
      id: 'vision_analyser', 
      position: { x: 300, y: 430 }, 
      data: { label: 'Vision Analyser Agent\nVLM: Pixtral-12B' }, 
      style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 22, width: 250 },  
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
      position: { x: 510, y: 10 }, 
      data: { label: 'WeatherAPI tool' }, 
      style: { background: '#a020f0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 400, fontSize: 24, width: 220 }, 
      targetPosition: Position.Left 
    },
    { 
      id: 'tool_calendarapi_list', 
      position: { x: 550, y: 80 }, 
      data: { label: 'CalendarAPI tool\nlist_events()' }, 
      style: { background: '#a020f0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 400, fontSize: 24, width: 220 }, 
      targetPosition: Position.Left 
    },
    { 
      id: 'tool_calendarapi_create', 
      position: { x: 560, y: 190 }, 
      data: { label: 'CalendarAPI tool\ncreate_event()' }, 
      style: { background: '#a020f0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 400, fontSize: 24, width: 220 }, 
      targetPosition: Position.Left 
    },
    { 
      id: 'tool_stravaapi', 
      position: { x: 550, y: 300 }, 
      data: { label: 'StravaAPI tool' }, 
      style: { background: '#a020f0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 400, fontSize: 24, width: 220 }, 
      targetPosition: Position.Left 
    },
    { 
      id: 'tool_chart', 
      position: { x: 560, y: 370 }, 
      data: { label: 'ChartCreator tool' }, 
      style: { background: '#a020f0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 400, fontSize: 24, width: 220 }, 
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
    },    { 
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
      source: 'planner', 
      target: 'tool_file_reader', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e6', 
      source: 'scheduler', 
      target: 'tool_weatherapi', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e7', 
      source: 'scheduler', 
      target: 'tool_calendarapi_list', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e8', 
      source: 'scheduler', 
      target: 'tool_calendarapi_create', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e9', 
      source: 'strava', 
      target: 'tool_stravaapi', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e10', 
      source: 'strava', 
      target: 'tool_chart', 
      sourceHandle: 'right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#a020f0', strokeWidth: 4 } 
    },
    { 
      id: 'e11', 
      source: 'analyser', 
      target: 'num_analyser', 
      sourceHandle: 'bottom', 
      targetHandle: 'top',
      animated: false, 
      style: { stroke: '#1565c0', strokeWidth: 4 } 
    },
    { 
      id: 'e12', 
      source: 'num_analyser', 
      target: 'vision_analyser', 
      sourceHandle: 'root-right', 
      targetHandle: 'left',
      animated: false, 
      style: { stroke: '#1565c0', strokeWidth: 4 } 
    }
  ];

// Log pattern to node mapping
const logPatternToNodes: { [key: string]: string[] } = {
  '[FRONTEND TO AGENT]': ['root'],
  '[PLANNER_AGENT]': ['planner'],
  '[SCHEDULER_AGENT]': ['scheduler'],
  '[STRAVA_AGENT]': ['strava'],
  '[NUMERICAL_ANALYSER_AGENT]': ['num_analyser'],
  '[VISION_ANALYSER_AGENT]': ['vision_analyser'],
  '[FileReader_tool]': ['tool_file_reader'],
  '[CalendarAPI_tool_create_event]': ['tool_calendarapi_create'],
  '[CalendarAPI_tool_list_events]': ['tool_calendarapi_list'],
  '[WeatherAPI_tool]': ['tool_weatherapi'],
  '[StravaAPI_tool]': ['tool_stravaapi'],
  '[ChartCreator_tool]': ['tool_chart'],

};

interface AgentFlowDiagramReactFlowProps {
  websocket?: WebSocket | null;
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

  // Function to highlight nodes based on log pattern
  const highlightNodesFromLog = useCallback((logMessage: string) => {
    console.log('Processing log message:', logMessage);
    
    // Check for agent START/FINISH events
    if (logMessage.includes('START:') || logMessage.includes('FINISH:')) {
      const agentMatch = logMessage.match(/\[(PLANNER_AGENT|SCHEDULER_AGENT|STRAVA_AGENT|ANALYSER_AGENT)\]/);
      if (agentMatch) {
        const agentName = agentMatch[1].toLowerCase().replace('_agent', '');
        console.log('Agent name extracted:', agentName);
        
        if (logMessage.includes('START:')) {
          setActiveAgents(prev => new Set(prev).add(agentName));
          
          // Highlight the agent node with animation
          setNodes(nds => nds.map(n => ({
            ...n,
            style: {
              ...n.style,
              boxShadow: n.id === agentName ? '0 0 16px 4px #68da81' : n.style?.boxShadow,
              zIndex: n.id === agentName ? 10 : n.style?.zIndex || 1,
            },
          })));
          
          // Animate connecting edges
          setEdges(eds => eds.map(e => ({
            ...e,
            animated: e.source === agentName || e.target === agentName,
            style: {
              ...e.style,
              stroke: (e.source === agentName || e.target === agentName) ? '#EA4335' : (e.style?.stroke || '#1976d2'),
              strokeWidth: (e.source === agentName || e.target === agentName) ? 4 : 2,
            },
          })));
        } else if (logMessage.includes('FINISH:')) {
          setActiveAgents(prev => {
            const newSet = new Set(prev);
            newSet.delete(agentName);
            return newSet;
          });
          
          // Remove highlighting from the agent node
          setNodes(nds => nds.map(n => ({
            ...n,
            style: {
              ...n.style,
              boxShadow: n.id === agentName ? undefined : n.style?.boxShadow,
              zIndex: n.id === agentName ? 1 : n.style?.zIndex || 1,
            },
          })));
          
          // Stop animating connecting edges
          setEdges(eds => eds.map(e => ({
            ...e,
            animated: e.source === agentName || e.target === agentName ? false : e.animated,
            style: {
              ...e.style,
              stroke: (e.source === agentName || e.target === agentName) ? (e.style?.stroke || '#1976d2') : e.style?.stroke,
              strokeWidth: (e.source === agentName || e.target === agentName) ? 2 : e.style?.strokeWidth,
            },
          })));
          
          // Clear all tool and root highlighting when an agent finishes
          setNodes(nds => nds.map(n => ({
            ...n,
            style: {
              ...n.style,
              boxShadow: (n.id.includes('api') || n.id === 'file_reader' || n.id === 'root') ? undefined : n.style?.boxShadow,
              zIndex: (n.id.includes('api') || n.id === 'file_reader' || n.id === 'root') ? 1 : n.style?.zIndex || 1,
            },
          })));
          
          // Reset all tool edges to normal
          setEdges(eds => eds.map(e => ({
            ...e,
            animated: false,
            style: {
              ...e.style,
              stroke: e.style?.stroke || '#1976d2',
              strokeWidth: 2,
            },
          })));
          
          setActiveNode(null);
        }
      }
    }
    
    // Handle tool events - highlight whenever tool name appears in log
    const matchingPattern = Object.keys(logPatternToNodes).find(pattern => 
      logMessage.includes(pattern) && !pattern.includes('_AGENT')
    );

    if (matchingPattern) {
      const nodesToHighlight = logPatternToNodes[matchingPattern];
      
      // Highlight the nodes
      setNodes(nds => nds.map(n => ({
        ...n,
        style: {
          ...n.style,
          boxShadow: nodesToHighlight.includes(n.id) ? '0 0 16px 4px #68da81' : n.style?.boxShadow,
          zIndex: nodesToHighlight.includes(n.id) ? 10 : n.style?.zIndex || 1,
        },
      })));

      // Highlight connecting edges
      setEdges(eds => eds.map(e => ({
        ...e,
        animated: true,
        style: {
          ...e.style,
          stroke: (e.source === nodesToHighlight[0] && e.target === nodesToHighlight[1]) || 
                  (e.source === nodesToHighlight[1] && e.target === nodesToHighlight[0]) 
                  ? '#EA4335' : e.style?.stroke,
          strokeWidth: (e.source === nodesToHighlight[0] && e.target === nodesToHighlight[1]) || 
                      (e.source === nodesToHighlight[1] && e.target === nodesToHighlight[0]) 
                      ? 4 : e.style?.strokeWidth || 2,
        },
      })));

      // Set active nodes for display
      setActiveNode(nodesToHighlight.join(', '));
      setLastLogTime(Date.now());
    }
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
            '[FileReader_tool]',
            '[ImageReader_tool]',
            '[CalendarAPI_tool_create_event]',
            '[CalendarAPI_tool_list_events]',
            '[WeatherAPI_tool]',
            '[StravaAPI_tool]',
            '[PLANNER_AGENT]',
            '[SCHEDULER_AGENT]',
            '[STRAVA_AGENT]',
            '[ANALYSER_AGENT]',
            '[NUMERICAL_ANALYSER_AGENT]',
            '[VISUAL_ANALYSER_AGENT]',
            '[ChartCreator_tool]',
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

  return (
    <div className="stat-card agent-flow-card" style={{ width: 440, height: 300, minHeight: 250, padding: '2px 0 2px 0', paddingLeft: 0 }}>
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
      >
        {/* <MiniMap /> and <Controls /> Removed for cleaner look */}
        <Background />
      </ReactFlow>
    </div>
  );
} 