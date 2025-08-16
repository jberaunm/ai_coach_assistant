import React from "react";
import { useSessionData } from "../contexts/SessionDataContext";

interface InsightsProps {
  date: Date;
}

// Simple markdown parser for basic formatting
const parseMarkdown = (text: string) => {
  if (!text) return text;
  
  // Split into lines for better processing
  const lines = text.split('\n');
  let result = [];
  let inList = false;
  let listItems = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (!line) {
      // Empty line - end current list if we're in one
      if (inList && listItems.length > 0) {
        result.push(renderList(listItems));
        listItems = [];
        inList = false;
      }
      result.push('<br>');
      continue;
    }
    
    // Check if this is a header
    if (line.startsWith('### ')) {
      if (inList && listItems.length > 0) {
        result.push(renderList(listItems));
        listItems = [];
        inList = false;
      }
      result.push(`<h3>${line.substring(4)}</h3>`);
      continue;
    }
    
    if (line.startsWith('## ')) {
      if (inList && listItems.length > 0) {
        result.push(renderList(listItems));
        listItems = [];
        inList = false;
      }
      result.push(`<h2>${line.substring(3)}</h2>`);
      continue;
    }
    
    if (line.startsWith('# ')) {
      if (inList && listItems.length > 0) {
        result.push(renderList(listItems));
        listItems = [];
        inList = false;
      }
      result.push(`<h1>${line.substring(2)}</h1>`);
      continue;
    }
    
    // Check if this is a numbered list item
    if (/^\d+\.\s/.test(line)) {
      inList = true;
      const content = line.replace(/^\d+\.\s/, '');
      listItems.push(`<li>${parseInlineMarkdown(content)}</li>`);
      continue;
    }
    
    // Check if this is a bullet list item
    if (/^[-*]\s/.test(line)) {
      inList = true;
      const content = line.replace(/^[-*]\s/, '');
      listItems.push(`<li>${parseInlineMarkdown(content)}</li>`);
      continue;
    }
    
    // If we were in a list but this line isn't a list item, end the list
    if (inList && listItems.length > 0) {
      result.push(renderList(listItems));
      listItems = [];
      inList = false;
    }
    
    // Regular paragraph text
    if (line) {
      result.push(`<p>${parseInlineMarkdown(line)}</p>`);
    }
  }
  
  // Don't forget to render any remaining list items
  if (inList && listItems.length > 0) {
    result.push(renderList(listItems));
  }
  
  return result.join('');
};

// Helper function to render lists
const renderList = (items: string[]) => {
  // Check if it's a numbered list (first item starts with a number)
  const isNumbered = /^\d+\./.test(items[0]);
  const tag = isNumbered ? 'ol' : 'ul';
  return `<${tag} class="${isNumbered ? 'numbered-list' : 'bullet-list'}">${items.join('')}</${tag}>`;
};

// Helper function to parse inline markdown (bold, italic)
const parseInlineMarkdown = (text: string) => {
  let parsed = text;
  // Handle bold text (**text**)
  parsed = parsed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Handle italic text (*text*)
  parsed = parsed.replace(/\*(.*?)\*/g, '<em>$1</em>');
  return parsed;
};

export default function Insights({ date }: InsightsProps) {
  const { sessionData, loading, error } = useSessionData();
  
  // Extract coach_feedback from session metadata
  const coachFeedback = sessionData?.metadata?.coach_feedback;

  if (loading) {
    return (
      <div className="stat-card insights-card">
        <h1>Insights</h1>
        <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
          Loading insights...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stat-card insights-card">
        <h1>Insights</h1>
        <div style={{ textAlign: "center", padding: "20px", color: "#f44336" }}>
          Error: {error}
        </div>
      </div>
    );
  }

  if (!coachFeedback) {
    return (
      <div className="stat-card insights-card">
        <h1>Insights</h1>
        <div style={{ 
          textAlign: "center", 
          padding: "20px", 
          color: "#666",
          fontStyle: "italic"
        }}>
          No insights available yet. Complete a training session to get personalized feedback and analysis.
        </div>
      </div>
    );
  }

  const parsedFeedback = parseMarkdown(coachFeedback);

  return (
    <div className="stat-card insights-card">
      <h1>Insights</h1>
      <div className="insights-content">
        <div 
          className="coach-feedback"
          dangerouslySetInnerHTML={{ __html: parsedFeedback }}
        />
      </div>
    </div>
  );
}
