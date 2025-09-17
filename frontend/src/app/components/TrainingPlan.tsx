"use client";
import React, { useRef, useState, useEffect } from "react";
import { useSessionData } from "../contexts/SessionDataContext";

interface TrainingPlan {
  id: string;
  goalPlan: string;
  raceDate?: string;
  age?: string;
  weight?: string;
  avgKmsPerWeek?: string;
  fastest5kTime?: string;
  createdAt: string;
  status: 'creating' | 'completed' | 'error';
  planDetails?: {
    totalWeeks?: number;
    totalSessions?: number;
    startDate?: string;
    endDate?: string;
  };
}

interface TrainingPlanProps {
  websocket: WebSocket | null;
}

export default function TrainingPlan({ websocket }: TrainingPlanProps) {
  const { sendMessage } = useSessionData();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<string>("");
  const [dragOver, setDragOver] = useState(false);
  const [hasUploadedPlan, setHasUploadedPlan] = useState(false);
  const [personalizedPlans, setPersonalizedPlans] = useState<TrainingPlan[]>([]);
  const [hasActivePlan, setHasActivePlan] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Fetch existing training plans on component mount
  useEffect(() => {
    const fetchTrainingPlans = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/training-plan-stats');
        const data = await response.json();
        
        if (data.status === 'success' && data.plans && data.plans.length > 0) {
          // Convert API data to TrainingPlan format
          const plans: TrainingPlan[] = data.plans.map((plan: any) => ({
            id: plan.plan_id || 'current_plan',
            goalPlan: 'Active Training Plan', // We don't store goal in the API yet
            raceDate: plan.end_date,
            createdAt: plan.created_at || new Date().toISOString(),
            status: 'completed' as const,
            planDetails: {
              totalWeeks: plan.duration_weeks,
              totalSessions: plan.total_sessions,
              startDate: plan.start_date,
              endDate: plan.end_date
            }
          }));
          
          setPersonalizedPlans(plans);
          setHasActivePlan(true);
        }
      } catch (error) {
        console.log('No existing training plans found or error fetching:', error);
      }
    };

    fetchTrainingPlans();
  }, []);

  // WebSocket message listener for planner_agent completion
  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        
        // Check if it's a log message with PLANNER_AGENT FINISH
        if (data.log_message && data.log_message.includes('[PLANNER_AGENT] FINISH:')) {
          console.log('Plan processing completed:', data.log_message);
          
          // Update the most recent creating plan to completed
          setPersonalizedPlans(prev => prev.map(plan => {
            if (plan.status === 'creating') {
              return {
                ...plan,
                status: 'completed' as const,
                planDetails: {
                  totalWeeks: 16, // Default values, could be extracted from response
                  totalSessions: 48,
                  startDate: new Date().toISOString().split('T')[0],
                  endDate: plan.raceDate || new Date(Date.now() + 16 * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
                }
              };
            }
            return plan;
          }));
          
          // Set hasActivePlan to true when plan is completed
          setHasActivePlan(true);
        }
        
        // Check if it's a log message with PLANNER_AGENT ERROR
        if (data.log_message && data.log_message.includes('[PLANNER_AGENT] ERROR:')) {
          console.log('Plan processing failed:', data.log_message);
          
          // Update the most recent creating plan to error
          setPersonalizedPlans(prev => prev.map(plan => {
            if (plan.status === 'creating') {
              return {
                ...plan,
                status: 'error' as const
              };
            }
            return plan;
          }));
        }
      } catch (error) {
        // Ignore non-JSON messages
      }
    };

    websocket.addEventListener('message', handleMessage);
    
    return () => {
      websocket.removeEventListener('message', handleMessage);
    };
  }, [websocket]);
  
  // Form state for personalized plan
  const [goalPlan, setGoalPlan] = useState<string>("");
  const [raceDate, setRaceDate] = useState<string>("");
  const [age, setAge] = useState<string>("");
  const [weight, setWeight] = useState<string>("");
  const [avgKmsPerWeek, setAvgKmsPerWeek] = useState<string>("");
  const [fastest5kTime, setFastest5kTime] = useState<string>("");

  const goalPlanOptions = [
    "General Fitness",
    "5k",
    "10k", 
    "Half-marathon",
    "Marathon",
    "Ultra-Marathon",
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'creating':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="animate-spin">
            <circle cx="12" cy="12" r="10" stroke="#3b82f6" strokeWidth="2" fill="none" strokeDasharray="31.416" strokeDashoffset="31.416">
              <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
              <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
            </circle>
          </svg>
        );
      case 'completed':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ color: "#10b981" }}>
            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        );
      case 'error':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ color: "#ef4444" }}>
            <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        );
      default:
        return null;
    }
  };

  const formatPlanTitle = (plan: TrainingPlan): string => {
    const raceDateFormatted = plan.raceDate 
      ? new Date(plan.raceDate).toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit' })
      : '';
    
    return `Training plan for ${plan.goalPlan}${raceDateFormatted ? ` on ${raceDateFormatted}` : ''}`;
  };

  const formatPlanDetails = (plan: TrainingPlan): string => {
    if (plan.status === 'creating') {
      return 'Creating personalized training plan...';
    }
    
    if (plan.status === 'error') {
      return 'Failed to create training plan';
    }

    const details = [];
    if (plan.age) details.push(`Age: ${plan.age}`);
    if (plan.weight) details.push(`Weight: ${plan.weight}kg`);
    if (plan.avgKmsPerWeek) details.push(`Weekly Volume: ${plan.avgKmsPerWeek}km`);
    if (plan.fastest5kTime) details.push(`5K Time: ${plan.fastest5kTime}`);
    
    return details.join(' • ');
  };

  const formatCreationDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDeleteTrainingPlan = async () => {
    if (isDeleting) return;
    
    const confirmed = window.confirm('Are you sure you want to delete the current training plan? This action cannot be undone.');
    if (!confirmed) return;
    
    setIsDeleting(true);
    setStatus("Deleting training plan...");
    
    try {
      const response = await fetch('http://localhost:8000/api/training-plan', {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setStatus("Training plan deleted successfully!");
        setPersonalizedPlans([]);
        setHasActivePlan(false);
        setHasUploadedPlan(false);
      } else {
        setStatus("Failed to delete training plan. Please try again.");
      }
    } catch (error) {
      console.error('Error deleting training plan:', error);
      setStatus("Failed to delete training plan. Please try again.");
    } finally {
      setIsDeleting(false);
      setTimeout(() => setStatus(""), 3000);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFiles = (files: FileList) => {
    if (!websocket) return;
    const file = files[0];
    if (!file) return;
    setStatus("Uploading...");
    const formData = new FormData();
    formData.append("file", file);
    // Get session ID from websocket URL
    let sessionId = "";
    try {
      const wsUrl = new URL(websocket.url);
      sessionId = wsUrl.pathname.split("/").pop() || "";
    } catch {}
    const uploadUrl = `http://localhost:8000/upload?session_id=${sessionId}`;
    // console.log("WebSocket URL used for upload:", websocket?.url);
    fetch(uploadUrl, { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setStatus("File uploaded successfully! Processing...");
          setHasUploadedPlan(true);
          setHasActivePlan(true);
          
          // Add processing entry to plans list
          const processingPlan: TrainingPlan = {
            id: Date.now().toString(),
            goalPlan: file.name.replace(/\.(csv|txt|doc|docx|md)$/i, ''),
            createdAt: new Date().toISOString(),
            status: 'creating'
          };
          
          setPersonalizedPlans(prev => [processingPlan, ...prev]);
        } else {
          setStatus("Upload failed. Please try again.");
        }
      })
      .catch(() => setStatus("Upload failed. Please try again."))
      .finally(() => {
        setTimeout(() => setStatus(""), 3000);
      });
  };

  const handleCreatePersonalizedPlan = () => {
    if (!sendMessage) {
      console.error("sendMessage function not available");
      setStatus("Error: Unable to send message");
      return;
    }

    if (!goalPlan) {
      setStatus("Please select a goal plan");
      setTimeout(() => setStatus(""), 3000);
      return;
    }

    // Create new plan entry
    const newPlan: TrainingPlan = {
      id: Date.now().toString(),
      goalPlan,
      raceDate,
      age,
      weight,
      avgKmsPerWeek,
      fastest5kTime,
      createdAt: new Date().toISOString(),
      status: 'creating'
    };

    // Add to plans list
    setPersonalizedPlans(prev => [newPlan, ...prev]);

    // Create the request message for planner_agent Workflow 2
    const requestMessage = `Create personalized training plan with:
    Goal Plan: ${goalPlan}
    ${raceDate ? `Race Date: ${raceDate}` : ''}
    ${age ? `Age: ${age}` : ''}
    ${weight ? `Weight: ${weight} kg` : ''}
    ${avgKmsPerWeek ? `Average KMs per Week: ${avgKmsPerWeek}` : ''}
    ${fastest5kTime ? `5K Fastest Time: ${fastest5kTime}` : ''}`;

    console.log("Creating personalized plan with:", {
      goalPlan,
      raceDate,
      age,
      weight,
      avgKmsPerWeek,
      fastest5kTime
    });

    // Send the message via WebSocket
    const success = sendMessage(requestMessage);
    
    if (success) {
      setStatus("Creating your personalized training plan...");
      console.log("Personalized plan request sent successfully");
    } else {
      setStatus("Failed to send request. Please try again.");
      // Update plan status to error
      setPersonalizedPlans(prev => prev.map(plan => 
        plan.id === newPlan.id ? { ...plan, status: 'error' as const } : plan
      ));
    }

    // Clear status after 5 seconds
    setTimeout(() => setStatus(""), 5000);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
      {/* Top Row - File Upload (only show if no active plan) */}
      {!hasActivePlan && (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <h2 style={{ 
            margin: "0 0 16px 0", 
            fontSize: "20px", 
            fontWeight: "600",
            color: "#1e293b"
          }}>
            Upload Training Plan
          </h2>
        
        <div
          className={`drop-zone${dragOver ? " dragover" : ""}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          style={{ 
            cursor: "pointer",
            border: "2px dashed #d1d5db",
            borderRadius: "8px",
            padding: "32px",
            textAlign: "center",
            backgroundColor: dragOver ? "#f3f4f6" : "#fafafa",
            transition: "all 0.2s ease"
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "12px" }}>
            {hasUploadedPlan ? (
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                style={{ color: "#10b981" }}
              >
                <path
                  d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            ) : (
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                style={{ color: "#6b7280" }}
              >
                <path
                  d="M12 5V19M5 12H19"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
            <p style={{ margin: 0, color: "#6b7280" }}>
              {status || "Drag and drop files here or click to upload"}
            </p>
          </div>
          <input
            type="file"
            id="fileUpload"
            ref={fileInputRef}
            hidden
            onChange={(e) => {
              if (e.target.files) handleFiles(e.target.files);
            }}
          />
        </div>
        
        {hasUploadedPlan && (
          <div style={{
            padding: "16px",
            backgroundColor: "#f8fafc",
            borderRadius: "8px",
            border: "1px solid #e2e8f0"
          }}>
            <h3 style={{ 
              margin: "0 0 8px 0", 
              fontSize: "16px", 
              fontWeight: "600",
              color: "#1e293b"
            }}>
              Training Plan Summary
            </h3>
            <div style={{ display: "flex", gap: "24px", fontSize: "14px" }}>
              <div>
                <span style={{ color: "#64748b" }}>Total Weeks: </span>
                <span style={{ fontWeight: "600", color: "#1e293b" }}>
                  12
                </span>
              </div>
              <div>
                <span style={{ color: "#64748b" }}>Total Workouts: </span>
                <span style={{ fontWeight: "600", color: "#1e293b" }}>
                  48
                </span>
              </div>
              <div>
                <span style={{ color: "#64748b" }}>File: </span>
                <span style={{ fontWeight: "600", color: "#1e293b" }}>
                  training_plan.csv
                </span>
              </div>
            </div>
          </div>
        )}
        </div>
      )}

      {/* Bottom Row - Personalized Plan Form (only show if no active plan) */}
      {!hasActivePlan && (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <h2 style={{ 
            margin: "0 0 16px 0", 
            fontSize: "20px", 
            fontWeight: "600",
            color: "#1e293b"
          }}>
            Create Personalized Plan
          </h2>
        
        <div style={{
          padding: "24px",
          backgroundColor: "#f8fafc",
          borderRadius: "8px",
          border: "1px solid #e2e8f0"
        }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* First Row: Goal Plan and Race Date */}
            <div style={{ display: "flex", gap: "16px" }}>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  Goal Plan *
                </label>
                <select
                  value={goalPlan}
                  onChange={(e) => setGoalPlan(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px",
                    backgroundColor: "white"
                  }}
                >
                  <option value="">Select your goal</option>
                  {goalPlanOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  Race Date
                </label>
                <input
                  type="date"
                  value={raceDate}
                  onChange={(e) => setRaceDate(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
              </div>
            </div>

            {/* Second Row: Age, Weight, and Average KMs */}
            <div style={{ display: "flex", gap: "16px" }}>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  Age
                </label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="25"
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  Weight (kg)
                </label>
                <input
                  type="number"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                  placeholder="70"
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  Average KMs per Week
                </label>
                <input
                  type="number"
                  value={avgKmsPerWeek}
                  onChange={(e) => setAvgKmsPerWeek(e.target.value)}
                  placeholder="20"
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
              </div>
            </div>

            {/* Third Row: 5K Time and Create Button */}
            <div style={{ display: "flex", gap: "16px", alignItems: "end" }}>
              <div style={{ flex: 1 }}>
                <label style={{ 
                  display: "block", 
                  marginBottom: "8px", 
                  fontSize: "14px", 
                  fontWeight: "500",
                  color: "#374151"
                }}>
                  5K Fastest Time (mm:ss)
                </label>
                <input
                  type="text"
                  value={fastest5kTime}
                  onChange={(e) => setFastest5kTime(e.target.value)}
                  placeholder="25:30"
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    fontSize: "14px"
                  }}
                />
              </div>
              <div style={{ flex: 1 }}>
                <button
                  onClick={handleCreatePersonalizedPlan}
                  disabled={!goalPlan}
                  style={{
                    width: "100%",
                    padding: "12px 24px",
                    backgroundColor: goalPlan ? "#3b82f6" : "#9ca3af",
                    color: "white",
                    border: "none",
                    borderRadius: "6px",
                    fontSize: "14px",
                    fontWeight: "500",
                    cursor: goalPlan ? "pointer" : "not-allowed",
                    transition: "background-color 0.2s ease"
                  }}
                >
                  Create Personalized Plan
                </button>
              </div>
            </div>
          </div>
        </div>
        </div>
      )}

      {/* Personalized Plans List */}
      {personalizedPlans.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ 
              margin: 0, 
              fontSize: "18px", 
              fontWeight: "600",
              color: "#1e293b"
            }}>
              Current Plan
            </h3>
            <span style={{ 
              fontSize: "14px", 
              color: "#6b7280",
              backgroundColor: "#f1f5f9",
              padding: "4px 8px",
              borderRadius: "4px"
            }}>
              {personalizedPlans.length} plan{personalizedPlans.length !== 1 ? 's' : ''}
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {personalizedPlans.map((plan) => (
              <div
                key={plan.id}
                style={{
                  padding: "16px",
                  backgroundColor: "white",
                  borderRadius: "8px",
                  border: "1px solid #e2e8f0",
                  boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    {getStatusIcon(plan.status)}
                    <span style={{ 
                      fontSize: "14px", 
                      fontWeight: "500",
                      color: plan.status === 'error' ? '#ef4444' : plan.status === 'creating' ? '#3b82f6' : '#1e293b'
                    }}>
                      {formatPlanTitle(plan)}
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ 
                      fontSize: "12px", 
                      color: "#6b7280"
                    }}>
                      {formatCreationDate(plan.createdAt)}
                    </span>
                    {plan.status === 'completed' && (
                      <button
                        onClick={handleDeleteTrainingPlan}
                        disabled={isDeleting}
                        style={{
                          padding: "4px 8px",
                          backgroundColor: "#ef4444",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          fontSize: "12px",
                          cursor: isDeleting ? "not-allowed" : "pointer",
                          opacity: isDeleting ? 0.6 : 1,
                          display: "flex",
                          alignItems: "center",
                          gap: "4px"
                        }}
                        title="Delete training plan"
                      >
                        {isDeleting ? (
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" className="animate-spin">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" strokeDasharray="31.416" strokeDashoffset="31.416">
                              <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                              <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
                            </circle>
                          </svg>
                        ) : (
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                            <path d="M19 7L18.1327 19.1425C18.0579 20.1891 17.187 21 16.1378 21H7.86224C6.81296 21 5.94208 20.1891 5.86732 19.1425L5 7M10 11V17M14 11V17M15 7V4C15 3.44772 14.5523 3 14 3H10C9.44772 3 9 3.44772 9 4V7M4 7H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        )}
{isDeleting ? "Deleting..." : ""}
                      </button>
                    )}
                  </div>
                </div>
                
                <div style={{ 
                  fontSize: "14px", 
                  lineHeight: "1.5",
                  color: "#374151"
                }}>
                  {formatPlanDetails(plan)}
                  
                  {/* Additional plan details for completed plans */}
                  {plan.status === 'completed' && plan.planDetails && (
                    <div style={{ 
                      marginTop: "8px", 
                      fontSize: "12px", 
                      color: "#6b7280",
                      display: "flex",
                      gap: "12px",
                      flexWrap: "wrap"
                    }}>
                      {plan.planDetails.totalWeeks && (
                        <span style={{
                          backgroundColor: "#dbeafe",
                          color: "#1e40af",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontSize: "11px",
                          fontWeight: "500"
                        }}>
                          {plan.planDetails.totalWeeks} weeks
                        </span>
                      )}
                      {plan.planDetails.totalSessions && (
                        <span style={{
                          backgroundColor: "#f3f4f6",
                          color: "#374151",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontSize: "11px"
                        }}>
                          {plan.planDetails.totalSessions} sessions
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
