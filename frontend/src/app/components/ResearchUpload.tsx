"use client";
import React, { useRef, useState, useEffect } from "react";

interface ResearchFile {
  id: string;
  documentId: string; // Add document ID for deletion
  filename: string;
  title: string;
  authors: string;
  year: string;
  journal: string;
  doi?: string;
  uploadedAt: string;
  status: 'processing' | 'completed' | 'error';
  // Additional metadata from RAG stats
  category?: string;
  chunkCount?: number;
  chunks?: Array<{
    chunk_id: string;
    title: string;
    content_preview: string;
  }>;
}

interface ResearchUploadProps {
  websocket?: WebSocket | null;
}

export default function ResearchUpload({ websocket }: ResearchUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [researchFiles, setResearchFiles] = useState<ResearchFile[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set());


  // Fetch existing research files on component mount
  useEffect(() => {
    const fetchResearchFiles = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/rag-stats');
        const data = await response.json();
        
        if (data.status === 'success' && data.sources) {
          // Convert sources to research files format using detailed metadata
          const files: ResearchFile[] = data.sources.map((source: any, index: number) => {
            const filename = source.source.split('/').pop() || 'Unknown file';
            const cleanTitle = source.document_title && source.document_title !== 'Unknown' 
              ? source.document_title 
              : filename.replace(/\.(pdf|txt|doc|docx|md)$/i, '');
            
            return {
              id: source.document_id || `source_${index}`,
              documentId: source.document_id || `source_${index}`,
              filename: filename,
              title: cleanTitle,
              authors: source.authors && source.authors !== 'Unknown' ? source.authors : undefined,
              year: source.document_year && source.document_year !== 'Unknown' ? source.document_year.toString() : undefined,
              journal: source.journal && source.journal !== 'Unknown' ? source.journal : undefined,
              doi: source.doi,
              uploadedAt: new Date().toISOString(),
              status: 'completed' as const,
              // Additional metadata for display
              category: source.category,
              chunkCount: source.chunk_count,
              chunks: source.chunks
            };
          });
          
          setResearchFiles(files);
        }
      } catch (error) {
        console.log('No existing research files found or error fetching:', error);
      }
    };

    fetchResearchFiles();
  }, []);

  // WebSocket message listener for RAG agent completion
  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        
        // Check if it's a log message with RAG_AGENT FINISH
        if (data.log_message && data.log_message.includes('[RAG_AGENT] FINISH:')) {
          console.log('RAG analysis completed:', data.log_message);
          
          // Refresh the research files data to get updated metadata
          const refreshResearchFiles = async () => {
            try {
              const response = await fetch('http://localhost:8000/api/rag-stats');
              const data = await response.json();
              
              if (data.status === 'success' && data.sources) {
                const files: ResearchFile[] = data.sources.map((source: any, index: number) => {
                  const filename = source.source.split('/').pop() || 'Unknown file';
                  const cleanTitle = source.document_title && source.document_title !== 'Unknown' 
                    ? source.document_title 
                    : filename.replace(/\.(pdf|txt|doc|docx|md)$/i, '');
                  
                  return {
                    id: source.document_id || `source_${index}`,
                    documentId: source.document_id || `source_${index}`,
                    filename: filename,
                    title: cleanTitle,
                    authors: source.authors && source.authors !== 'Unknown' ? source.authors : undefined,
                    year: source.document_year && source.document_year !== 'Unknown' ? source.document_year.toString() : undefined,
                    journal: source.journal && source.journal !== 'Unknown' ? source.journal : undefined,
                    doi: source.doi,
                    uploadedAt: new Date().toISOString(),
                    status: 'completed' as const,
                    category: source.category,
                    chunkCount: source.chunk_count,
                    chunks: source.chunks
                  };
                });
                
                setResearchFiles(files);
              }
            } catch (error) {
              console.log('Error refreshing research files:', error);
            }
          };
          
          refreshResearchFiles();
        }
        
        // Check if it's a log message with RAG_AGENT ERROR
        if (data.log_message && data.log_message.includes('[RAG_AGENT] ERROR:')) {
          console.log('RAG analysis failed:', data.log_message);
          
          // Update the most recent processing file to error
          setResearchFiles(prev => prev.map(file => {
            if (file.status === 'processing') {
              return {
                ...file,
                status: 'error' as const,
                title: file.filename.replace('.pdf', '').replace('.txt', '').replace('.doc', '').replace('.docx', '').replace('.md', ''),
                authors: "Analysis failed",
                year: new Date().getFullYear().toString(),
                journal: "Error processing"
              };
            }
            return file;
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

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFiles = (files: FileList) => {
    const file = files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['.pdf', '.txt', '.doc', '.docx', '.md'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      setUploadStatus("Please upload a PDF, TXT, DOC, DOCX, or MD file");
      setTimeout(() => setUploadStatus(""), 3000);
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setUploadStatus("File size must be less than 10MB");
      setTimeout(() => setUploadStatus(""), 3000);
      return;
    }

    setUploadStatus("Uploading research file...");
    setIsLoading(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("type", "research");

    // Get session ID from websocket URL
    let sessionId = "";
    try {
      if (websocket) {
        const wsUrl = new URL(websocket.url);
        sessionId = wsUrl.pathname.split("/").pop() || "";
      }
    } catch {}

    const uploadUrl = `http://localhost:8000/upload-research?session_id=${sessionId}`;

    fetch(uploadUrl, { 
      method: "POST", 
      body: formData 
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setUploadStatus("Research file uploaded successfully! Processing...");
          
          // Add to local state as processing
          const newFile: ResearchFile = {
            id: Date.now().toString(),
            documentId: Date.now().toString(), // Temporary ID for processing files
            filename: file.name,
            title: "Processing...",
            authors: "Processing...",
            year: "Processing...",
            journal: "Processing...",
            uploadedAt: new Date().toISOString(),
            status: 'processing'
          };
          
          setResearchFiles(prev => [newFile, ...prev]);
          
          // No need to send manual message - the backend handles it automatically
        } else {
          setUploadStatus("Upload failed. Please try again.");
        }
      })
      .catch(() => setUploadStatus("Upload failed. Please try again."))
      .finally(() => {
        setIsLoading(false);
        setTimeout(() => setUploadStatus(""), 5000);
      });
  };

  const formatHarvardCitation = (file: ResearchFile): string => {
    if (file.status === 'processing') {
      return `${file.filename} (Processing...)`;
    }
    
    if (file.status === 'error') {
      return `${file.filename} (Error processing)`;
    }

    const parts: string[] = [];
    
    // Add authors if available and not "Unknown"
    if (file.authors && file.authors !== "Unknown" && file.authors !== "Unknown authors") {
      parts.push(file.authors);
    }
    
    // Add year if available and not "Unknown"
    if (file.year && file.year !== "Unknown" && file.year !== new Date().getFullYear().toString()) {
      parts.push(`(${file.year})`);
    }
    
    // Add title if available and not "Unknown"
    if (file.title && file.title !== "Unknown" && file.title !== "Untitled") {
      parts.push(file.title);
    }
    
    // Add journal if available and not "Unknown"
    if (file.journal && file.journal !== "Unknown" && file.journal !== "RAG Knowledge Base") {
      parts.push(`<em>${file.journal}</em>`);
    }
    
    // Add DOI if available
    if (file.doi) {
      parts.push(`DOI: ${file.doi}`);
    }
    
    // If no meaningful data, show filename
    if (parts.length === 0) {
      return file.filename;
    }
    
    return parts.join(". ");
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing':
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

  const formatUploadDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDeleteRAGEntry = async (fileId: string, documentId: string) => {
    if (deletingIds.has(fileId)) return;
    
    const confirmed = window.confirm('Are you sure you want to delete this research file? This action cannot be undone.');
    if (!confirmed) return;
    
    setDeletingIds(prev => new Set(prev).add(fileId));
    
    try {
      const response = await fetch(`http://localhost:8000/api/rag-entry/${documentId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setResearchFiles(prev => prev.filter(file => file.id !== fileId));
        setUploadStatus("Research file deleted successfully!");
      } else {
        setUploadStatus("Failed to delete research file. Please try again.");
      }
    } catch (error) {
      console.error('Error deleting RAG entry:', error);
      setUploadStatus("Failed to delete research file. Please try again.");
    } finally {
      setDeletingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
      setTimeout(() => setUploadStatus(""), 3000);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", width: "450px" }}>
      {/* Upload Section */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <h2 style={{ 
          margin: "0 0 0 0", 
          fontSize: "20px", 
          fontWeight: "600",
          color: "#1e293b"
        }}>
          Upload Research Files
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
            padding: "0",
            textAlign: "center",
            backgroundColor: dragOver ? "#f3f4f6" : "#fafafa",
            transition: "all 0.2s ease"
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "12px" }}>
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              style={{ color: "#6b7280" }}
            >
              <path
                d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M14 2V8H20"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M16 13H8"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M16 17H8"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M10 9H8"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div>
              <p style={{ margin: "0 0 4px 0", color: "#6b7280", fontWeight: "500" }}>
                {uploadStatus || "Drag and drop research files here or click to upload"}
              </p>
              <p style={{ margin: 0, fontSize: "14px", color: "#9ca3af" }}>
                Supports PDF, TXT, DOC, DOCX, MD (max 10MB)
              </p>
            </div>
          </div>
          <input
            type="file"
            ref={fileInputRef}
            hidden
            accept=".pdf,.txt,.doc,.docx,.md"
            onChange={(e) => {
              if (e.target.files) handleFiles(e.target.files);
            }}
          />
        </div>
      </div>

      {/* Research Files List */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ 
            margin: 0, 
            fontSize: "18px", 
            fontWeight: "600",
            color: "#1e293b"
          }}>
            Research Knowledge Base
          </h3>
          <span style={{ 
            fontSize: "14px", 
            color: "#6b7280",
            backgroundColor: "#f1f5f9",
            padding: "4px 8px",
            borderRadius: "4px"
          }}>
            {researchFiles.length} file{researchFiles.length !== 1 ? 's' : ''}
          </span>
        </div>

        {researchFiles.length === 0 ? (
          <div style={{
            padding: "32px",
            textAlign: "center",
            backgroundColor: "#f8fafc",
            borderRadius: "8px",
            border: "1px solid #e2e8f0"
          }}>
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              style={{ color: "#cbd5e1", margin: "0 auto 16px" }}
            >
              <path
                d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <p style={{ margin: 0, color: "#64748b" }}>
              No research files uploaded yet. Upload your first research paper to build your knowledge base.
            </p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {researchFiles.map((file) => (
              <div
                key={file.id}
                style={{
                  padding: "16px",
                  backgroundColor: "white",
                  borderRadius: "8px",
                  border: "1px solid #e2e8f0",
                  boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                  <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", flex: 1, minWidth: 0 }}>
                    {getStatusIcon(file.status)}
                    <span style={{ 
                      fontSize: "14px", 
                      fontWeight: "500",
                      color: file.status === 'error' ? '#ef4444' : file.status === 'processing' ? '#3b82f6' : '#1e293b',
                      wordBreak: "break-all",
                      overflowWrap: "break-word",
                      lineHeight: "1.4"
                    }}>
                      {file.filename}
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", flexShrink: 0 }}>
                    <span style={{ 
                      fontSize: "12px", 
                      color: "#6b7280"
                    }}>
                      {formatUploadDate(file.uploadedAt)}
                    </span>
                    {file.status === 'completed' && (
                      <button
                        onClick={() => handleDeleteRAGEntry(file.id, file.documentId)}
                        disabled={deletingIds.has(file.id)}
                        style={{
                          padding: "4px 8px",
                          backgroundColor: "#ef4444",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          fontSize: "12px",
                          cursor: deletingIds.has(file.id) ? "not-allowed" : "pointer",
                          opacity: deletingIds.has(file.id) ? 0.6 : 1,
                          display: "flex",
                          alignItems: "center",
                          gap: "4px"
                        }}
                        title="Delete research file"
                      >
                        {deletingIds.has(file.id) ? (
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
{deletingIds.has(file.id) ? "Deleting..." : ""}
                      </button>
                    )}
                  </div>
                </div>
                
                <div style={{ 
                  fontSize: "14px", 
                  lineHeight: "1.5",
                  color: "#374151"
                }}>
                  <div dangerouslySetInnerHTML={{ 
                    __html: formatHarvardCitation(file) 
                  }} />
                  
                  {/* Additional metadata display */}
                  {file.status === 'completed' && (
                    <div style={{ 
                      marginTop: "8px", 
                      fontSize: "12px", 
                      color: "#6b7280",
                      display: "flex",
                      gap: "12px",
                      flexWrap: "wrap"
                    }}>
                      {file.category && (
                        <span style={{
                          backgroundColor: file.category === 'Training_Plan' ? '#dbeafe' : '#fef3c7',
                          color: file.category === 'Training_Plan' ? '#1e40af' : '#92400e',
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontSize: "11px",
                          fontWeight: "500"
                        }}>
                          {file.category === 'Training_Plan' ? 'Training Plan' : 'Session Analysis'}
                        </span>
                      )}
                      {file.chunkCount && (
                        <span style={{
                          backgroundColor: "#f3f4f6",
                          color: "#374151",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontSize: "11px"
                        }}>
                          {file.chunkCount} chunk{file.chunkCount !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
