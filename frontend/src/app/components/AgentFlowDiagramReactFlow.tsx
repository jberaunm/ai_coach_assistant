import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { Node as RFNode } from 'reactflow';

const initialNodes: Node[] = [
  { id: 'root', position: { x: -10, y: 150 }, data: { label: 'Root Agent\nGemini' }, type: 'input', style: { background: '#1976d2', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 24, width: 220 }, sourcePosition: Position.Right },
  { id: 'planner', position: { x: 260, y: 0 }, data: { label: 'Planner_agent\nMistralAI' }, style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 24, width: 220 }, sourcePosition: Position.Right, targetPosition: Position.Left },
  { id: 'scheduler', position: { x: 260, y: 150 }, data: { label: 'Scheduler_agent\nMistralAI' }, style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 24, width: 220 }, sourcePosition: Position.Right, targetPosition: Position.Left },
  { id: 'strava', position: { x: 260, y: 300 }, data: { label: 'Strava_agent\nMistralAI' }, style: { background: '#1565c0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 24, width: 220 }, sourcePosition: Position.Right, targetPosition: Position.Left },
  { id: 'weatherapi', position: { x: 510, y: -20 }, data: { label: 'WeatherAPI tool' }, style: { background: '#a020f0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 24, width: 220 }, targetPosition: Position.Left },
  { id: 'calendarapi', position: { x: 510, y: 100 }, data: { label: 'Google CalendarAPI tool' }, style: { background: '#a020f0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 24, width: 220 }, targetPosition: Position.Left },
  { id: 'stravaapi', position: { x: 510, y: 300 }, data: { label: 'StravaAPI tool' }, style: { background: '#a020f0', color: '#fff', borderRadius: 8, padding: 8, fontWeight: 600, fontSize: 24, width: 220 }, targetPosition: Position.Left },
];

const initialEdges: Edge[] = [
  { id: 'e1', source: 'root', target: 'planner', animated: true, style: { strokeWidth: 2 } },
  { id: 'e2', source: 'root', target: 'scheduler', animated: true, style: { strokeWidth: 2 } },
  { id: 'e3', source: 'root', target: 'strava', animated: true, style: { strokeWidth: 2 } },
  { id: 'e5', source: 'planner', target: 'weatherapi', animated: true, style: { stroke: '#a020f0', strokeWidth: 2 } },
  { id: 'e6', source: 'scheduler', target: 'calendarapi', animated: true, style: { stroke: '#a020f0', strokeWidth: 2 } },
  { id: 'e7', source: 'strava', target: 'stravaapi', animated: true, style: { stroke: '#a020f0', strokeWidth: 2 } },
];

export default function AgentFlowDiagramReactFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [activeEdge, setActiveEdge] = useState<string | null>(null);
  const [activeNode, setActiveNode] = useState<string | null>(null);

  // Mock live update: animate a task being handed over every 2 seconds
  useEffect(() => {
    const edgeOrder = ['e1', 'e2', 'e3', 'e5', 'e6', 'e7'];
    let idx = 0;
    const interval = setInterval(() => {
      setActiveEdge(edgeOrder[idx % edgeOrder.length]);
      setActiveNode(initialEdges.find(e => e.id === edgeOrder[idx % edgeOrder.length])?.target || null);
      idx++;
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Highlight active edge and node
  useEffect(() => {
    setEdges(eds => eds.map(e => ({
      ...e,
      animated: true,
      style: {
        ...e.style,
        stroke: e.id === activeEdge ? '#EA4335' : (e.style?.stroke || '#1976d2'),
        strokeWidth: e.id === activeEdge ? 4 : 2,
      },
    })));
    setNodes(nds => nds.map(n => ({
      ...n,
      style: {
        ...n.style,
        boxShadow: n.id === activeNode ? '0 0 16px 4px #EA4335' : undefined,
        zIndex: n.id === activeNode ? 10 : 1,
      },
    })));
  }, [activeEdge, activeNode, setEdges, setNodes]);

  // Node click handler for interactivity
  const onNodeClick = useCallback((event: React.MouseEvent, node: RFNode) => {
    alert(`Clicked on ${node.data.label}`);
  }, []);

  return (
    <div className="stat-card agent-flow-card" style={{ width: 440, height: 250, minHeight: 250, padding: '2px 0 2px 0', paddingLeft: 0 }}>
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
      >
        {/* <MiniMap /> and <Controls /> Removed for cleaner look */}
        <Background />
      </ReactFlow>
    </div>
  );
} 