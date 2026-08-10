import { useState, useEffect, useRef } from "react";
import axios from "axios";
import Spinner from "../components/Spinner";
import Cookies from "js-cookie";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
import Header from "../components/Header";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";
import { Send, Bot, User as UserIcon, FileText, ChevronDown, ChevronUp, Lock } from "lucide-react";

interface QAItem {
  question: string;
  answer: string;
}

interface DocumentDetails {
  alias: string;
  summary: string;
  filetype: string;
  created_at: string;
  transcription?: string;
  is_confidential: string; 
}

const token = Cookies.get("token");

const Chats: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const [loading, setLoading] = useState(false);
  const [documentDetails, setDocumentDetails] = useState<DocumentDetails | null>(null);
  const [qas, setQas] = useState<QAItem[]>([]);
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);

  const [unlock, setUnlock] = useState(false);
  const [unlockPassword, setUnlockPassword] = useState("");
  const [showDocDetails, setShowDocDetails] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [qas]);

  useEffect(() => {
    const fetchDocumentDetails = async () => {
      try {
        setLoading(true);
        const res = await axios.get(`${API_BASE}/documents/${documentId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setDocumentDetails(res.data);
      } catch (error) {
        console.error("Error fetching document details:", error);
      } finally {
        setLoading(false);
      }
    };
    
    // Also load initial chats
    const loadChats = async () => {
      try {
        const res = await axios.get(`${API_BASE}/qnaAll?document_id=${documentId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setQas(res.data);
      } catch (error) {
        console.error("Error loading chats:", error);
      }
    };

    fetchDocumentDetails();
    loadChats();
  }, [documentId, API_BASE]);

  const handleAsk = async () => {
    if (!question.trim()) return;

    if (documentDetails?.is_confidential === "yes" && !unlock) {
      toast.warning("Unlock this document to start asking questions.");
      return;
    }

    const currentQuestion = question;
    setQuestion("");
    setSending(true);

    // Optimistically add user question (without answer yet)
    setQas((prev) => [...prev, { question: currentQuestion, answer: "" }]);

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          document_id: documentId,
          question: currentQuestion,
        }),
      });

      if (!res.ok) throw new Error("Network response was not ok");

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done && reader) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          
          setQas((prev) => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            updated[updated.length - 1] = {
              ...lastMsg,
              answer: (lastMsg.answer || "") + chunk,
            };
            return updated;
          });
        }
      }
      
    } catch (error) {
      console.error("Error asking question:", error);
      toast.error("Failed to get an answer.");
      // Remove optimistic update on failure
      setQas((prev) => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  const handleUnlock = async () => {
    if (!unlockPassword.trim()) {
      toast.error("Please enter a password.");
      return;
    }
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.post(`${API_BASE}/documents/${documentId}/unlock`, {
        password: unlockPassword,
      }, { headers });
      const { summary, transcription } = res.data;
      setDocumentDetails(prev => ({
        ...prev!,
        summary: summary,
        transcription: transcription,
      }));
      setUnlock(true);
      toast.success("Document unlocked successfully!");
    } catch (error) {
      toast.error("Failed to unlock document.");
      console.error("Unlock error:", error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-50">
        <Spinner message="Loading your chats" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header Area */}
      <div className="bg-white shadow-sm z-10 p-4 border-b">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
            <Header />
            <h1 className="text-xl font-semibold text-gray-800">InsightFlow Chat</h1>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8">
        <div className="max-w-3xl mx-auto space-y-6">
          
          {/* Document Context Accordion */}
          {documentDetails && (
            <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
              <button 
                onClick={() => setShowDocDetails(!showDocDetails)}
                className="w-full p-4 flex justify-between items-center bg-gray-50 hover:bg-gray-100 transition"
              >
                <div className="flex items-center text-gray-700 font-medium">
                  <FileText className="w-5 h-5 mr-2 text-blue-500" />
                  {documentDetails.alias}
                </div>
                {showDocDetails ? <ChevronUp className="w-5 h-5 text-gray-500" /> : <ChevronDown className="w-5 h-5 text-gray-500" />}
              </button>
              
              {showDocDetails && (
                <div className="p-4 border-t text-sm text-gray-600 bg-white">
                  {documentDetails.is_confidential === "yes" && !unlock ? (
                     <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                        <div className="flex items-center text-red-600 font-medium mb-3">
                            <Lock className="w-4 h-4 mr-2" /> This document is confidential.
                        </div>
                        <div className="flex gap-2">
                            <input
                                type="password"
                                placeholder="Enter password"
                                className="flex-1 border p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-red-400"
                                value={unlockPassword}
                                onChange={(e) => setUnlockPassword(e.target.value)}
                            />
                            <button
                                onClick={handleUnlock}
                                className="bg-red-600 hover:bg-red-700 transition text-white px-4 py-2 rounded-md"
                            >
                                Unlock
                            </button>
                        </div>
                     </div>
                  ) : (
                      <div className="space-y-3">
                          <p><strong>Summary:</strong> {documentDetails.summary}</p>
                      </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Chat Messages */}
          {qas.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-gray-400">
              <Bot className="w-12 h-12 mb-3 text-gray-300" />
              <p>No messages yet. Start a conversation!</p>
            </div>
          ) : (
            <div className="space-y-6 pb-20">
              {qas.map((qa, index) => (
                <div key={index} className="space-y-6">
                  {/* User Message */}
                  <div className="flex justify-end">
                    <div className="bg-blue-600 text-white p-4 rounded-2xl rounded-tr-none max-w-[85%] shadow-sm">
                      <div className="flex items-center mb-1 text-blue-100 text-xs">
                         <UserIcon className="w-3 h-3 mr-1" /> You
                      </div>
                      <p className="whitespace-pre-wrap">{qa.question}</p>
                    </div>
                  </div>

                  {/* AI Message */}
                  <div className="flex justify-start">
                    <div className="bg-white border text-gray-800 p-5 rounded-2xl rounded-tl-none max-w-[85%] shadow-sm">
                      <div className="flex items-center mb-2 text-gray-400 text-xs font-semibold uppercase tracking-wider">
                         <Bot className="w-3 h-3 mr-1" /> InsightFlow AI
                      </div>
                      {qa.answer ? (
                        <div className="prose prose-sm md:prose-base prose-blue max-w-none">
                            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                              {qa.answer}
                            </ReactMarkdown>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2 h-6">
                           <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce"></div>
                           <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                           <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t p-4 z-10 w-full shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
        <div className="max-w-3xl mx-auto relative flex items-center">
          <input
            type="text"
            placeholder="Ask a question about this document..."
            className="flex-1 border bg-gray-50 border-gray-200 p-4 pr-14 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition shadow-inner"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleAsk(); }}
            disabled={sending || (documentDetails?.is_confidential === "yes" && !unlock)}
          />
          <button
            className={`absolute right-2 p-2 rounded-xl transition ${
                sending || !question.trim() ? "text-gray-400 bg-gray-100 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700 shadow-md"
            }`}
            onClick={handleAsk}
            disabled={sending || !question.trim() || (documentDetails?.is_confidential === "yes" && !unlock)}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chats;
