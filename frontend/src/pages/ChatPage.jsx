import React, { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import ChatWindow from "../components/ChatWindow";
import api from "../services/api";

const fallbackPersonas = [
  {
    key: "persona-family-buyer",
    name: "Sarah & Mike Jenkins",
    persona_type: "family",
    budget_range: "$35,000 - $45,000",
    personality: "Practical, safety-first, family-focused",
    preferences: ["Spacious cabin", "Top crash safety ratings", "Warranty coverage"],
    goals: ["Seating for kids", "Large cargo capacity"],
    pain_points: ["Being pressured on add-ons"],
    sympathy_level: "High Sympathy"
  },
  {
    key: "persona-budget-buyer",
    name: "Alex Thompson",
    persona_type: "budget",
    budget_range: "$18,000 - $25,000",
    personality: "Cautious, price-sensitive, researched",
    preferences: ["Lowest possible MSRP", "High fuel efficiency", "Bluetooth standard"],
    goals: ["Affordable commuter", "Low financing cost"],
    pain_points: ["Hidden fees, extra features"],
    sympathy_level: "Low Sympathy"
  },
  {
    key: "persona-performance-enthusiast",
    name: "Marcus Vance",
    persona_type: "performance",
    budget_range: "$40,000 - $55,000",
    personality: "Enthusiastic, demanding, specs-driven",
    preferences: ["Turbo engine", "Paddle shifters", "Sport suspension"],
    goals: ["Speed and dynamic response", "Advanced connectivity"],
    pain_points: ["Lacking power, slow transmission"],
    sympathy_level: "Moderate Sympathy"
  },
  {
    key: "persona-eco-conscious-buyer",
    name: "Elena Rostova",
    persona_type: "eco",
    budget_range: "$30,000 - $40,000",
    personality: "Eco-conscious, quiet, analytical",
    preferences: ["EV/Hybrid", "Regenerative braking", "Eco materials"],
    goals: ["Low fuel usage", "Reduced emissions"],
    pain_points: ["Lack of charge network info"],
    sympathy_level: "Moderate Sympathy"
  }
];

const fallbackVehicles = [
  {
    key: "kia-seltos-2025",
    make: "Kia",
    model: "Seltos",
    year: 2025,
    msrp: 24500,
    category: "Compact SUV",
    features: ["All-Wheel Drive Option", "Kia Drive Wise Suite", "10.25-inch Touchscreen"]
  },
  {
    key: "kia-sonet-2025",
    make: "Kia",
    model: "Sonet",
    year: 2025,
    msrp: 19900,
    category: "Subcompact SUV",
    features: ["Rear-View Camera", "Wireless Apple CarPlay", "32 MPG High Economy"]
  },
  {
    key: "kia-carens-2025",
    make: "Kia",
    model: "Carens",
    year: 2025,
    msrp: 31000,
    category: "Recreational Multi-Utility Vehicle",
    features: ["3-Row 7-Passenger Seating", "Electric One-Touch Seats", "6 Airbags Standard"]
  }
];

function ChatPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const personaKey = searchParams.get("personaKey");
  const vehicleKey = searchParams.get("vehicleKey");

  const [activePersona, setActivePersona] = useState(null);
  const [activeVehicle, setActiveVehicle] = useState(null);

  // Conversation States
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [isSending, setIsSending] = useState(false);

  // Live Coaching & Evaluation Metrics States
  const [coachingFeedback, setCoachingFeedback] = useState("");
  const [conversationStage, setConversationStage] = useState("greeting");
  const [decisionState, setDecisionState] = useState({
    customer_mood: "interested",
    recommended_action: "Introduce yourself and ask open-ended questions"
  });
  const [evaluation, setEvaluation] = useState({
    communication: 0,
    product_knowledge: 0,
    needs_analysis: 0,
    pricing_accuracy: 0,
    professionalism: 0
  });

  // Load Persona and Vehicle configurations
  useEffect(() => {
    if (!personaKey || !vehicleKey) return;

    async function loadConfig() {
      try {
        const [personasRes, vehiclesRes] = await Promise.all([
          api.get("/personas").catch(() => ({ data: [] })),
          api.get("/vehicles").catch(() => ({ data: [] }))
        ]);

        const plist = personasRes.data.length > 0 ? personasRes.data : fallbackPersonas;
        const vlist = vehiclesRes.data.length > 0 ? vehiclesRes.data : fallbackVehicles;

        const personaConfig = plist.find(p => (p.key === personaKey || p.id === personaKey));
        const vehicleConfig = vlist.find(v => (v.key === vehicleKey || v.id === vehicleKey));

        setActivePersona(personaConfig || fallbackPersonas.find(p => p.key === personaKey) || fallbackPersonas[0]);
        setActiveVehicle(vehicleConfig || fallbackVehicles.find(v => v.key === vehicleKey) || fallbackVehicles[0]);
      } catch (err) {
        console.warn("Failed to query configurations. Utilizing fallbacks.", err);
        setActivePersona(fallbackPersonas.find(p => p.key === personaKey) || fallbackPersonas[0]);
        setActiveVehicle(fallbackVehicles.find(v => v.key === vehicleKey) || fallbackVehicles[0]);
      }
    }
    loadConfig();
  }, [personaKey, vehicleKey]);

  // Send message turn via HTTP REST API
  const handleSendMessage = async (text) => {
    if (isSending || !text.trim() || !activePersona || !activeVehicle) return;

    const userMessage = {
      role: "user",
      content: text,
      timestamp: new Date().toISOString()
    };

    // Update conversation log locally with salesperson message
    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);

    try {
      const response = await api.post("/test/conversation", {
        persona_key: activePersona.key || personaKey,
        vehicle_key: activeVehicle.key || vehicleKey,
        message: text,
        session_external_id: sessionId
      });

      if (response.data) {
        // Capture session ID for subsequent turns to persist history on the backend
        if (response.data.session_external_id) {
          setSessionId(response.data.session_external_id);
        }

        // Add Customer message to dialogue log
        const customerMessage = {
          role: "assistant",
          content: response.data.customer_reply || "...",
          timestamp: new Date().toISOString()
        };
        setMessages((prev) => [...prev, customerMessage]);

        // Update real-time metrics and coaching feedback panels
        if (response.data.coaching_feedback) {
          setCoachingFeedback(response.data.coaching_feedback);
        }
        if (response.data.conversation_stage) {
          setConversationStage(response.data.conversation_stage);
        }
        if (response.data.decision_state) {
          setDecisionState({
            customer_mood: response.data.decision_state.customer_mood || "neutral",
            recommended_action: response.data.decision_state.recommended_action || "Ask open discovery questions"
          });
        }
        if (response.data.evaluation) {
          setEvaluation({
            communication: response.data.evaluation.communication || 0,
            product_knowledge: response.data.evaluation.product_knowledge || 0,
            needs_analysis: response.data.evaluation.needs_analysis || 0,
            pricing_accuracy: response.data.evaluation.pricing_accuracy || 0,
            professionalism: response.data.evaluation.professionalism || 0
          });
        }
      }
    } catch (err) {
      console.error("Error executing dialogue turn:", err);
      // Fail gracefully: display system notice
      setMessages((prev) => [...prev, {
        role: "system",
        content: "Dialogue turn failed due to network connection timeouts or backend database configuration issues.",
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsSending(false);
    }
  };

  const handleEndSession = async () => {
    // If no sessionId has been generated yet, we navigate back directly
    if (!sessionId) {
      navigate("/");
      return;
    }

    try {
      // Trigger final scoring and report generation
      await api.post(`/sessions/${sessionId}/evaluate`);
      navigate(`/reports?sessionId=${sessionId}`);
    } catch (err) {
      console.error("Failed to submit session evaluation. Proceeding to reports page.", err);
      navigate(`/reports?sessionId=${sessionId}`);
    }
  };

  if (!personaKey || !vehicleKey) {
    return (
      <div className="chat-empty-setup">
        <h2>Practice Room</h2>
        <p>No active training configuration found. Choose a persona and vehicle from the dashboard to begin.</p>
        <button type="button" className="btn-primary" onClick={() => navigate("/")} style={{ marginTop: "16px" }}>
          Go to Dashboard
        </button>
      </div>
    );
  }

  if (!activePersona || !activeVehicle) {
    return <div className="loading-state">Initialising session metadata...</div>;
  }

  return (
    <div className="chat-layout">
      {/* Column 1: Left Sidebar - Customer Profile Info */}
      <div className="chat-sidebar left-sidebar">
        <div className="glass-card sidebar-card customer-profile-card">
          <div className="card-badge-header">
            <span className="badge badge-info">{activePersona.persona_type || "standard"}</span>
          </div>
          <h3 className="profile-title">{activePersona.name}</h3>
          
          <div className="profile-details">
            <div className="detail-item">
              <span className="detail-label">Personality Type:</span>
              <span className="detail-val">{activePersona.personality}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Sympathy Guideline:</span>
              <span className="detail-val">{activePersona.sympathy_level || "Moderate Sympathy"}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Budget Constraints:</span>
              <span className="detail-val">{activePersona.budget_range}</span>
            </div>
            
            <div className="profile-list-section">
              <strong>Goals:</strong>
              <ul>
                {activePersona.goals?.map((g, idx) => <li key={idx}>{g}</li>)}
              </ul>
            </div>

            <div className="profile-list-section">
              <strong>Pain Points:</strong>
              <ul>
                {activePersona.pain_points?.map((p, idx) => <li key={idx}>{p}</li>)}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Column 2: Center Main - Chat Conversation */}
      <div className="chat-main-view">
        <div className="active-vehicle-bar">
          <span>Practice Vehicle: <strong>{activeVehicle.year} {activeVehicle.make} {activeVehicle.model}</strong> (${activeVehicle.msrp.toLocaleString()})</span>
        </div>
        <ChatWindow
          messages={messages}
          onSendMessage={handleSendMessage}
          onEndSession={handleEndSession}
          isConnected={!isSending}
          coachingFeedback={coachingFeedback}
        />
      </div>

      {/* Column 3: Right Sidebar - Live Evaluation & Scorecards */}
      <div className="chat-sidebar right-sidebar">
        {/* Session Summary Card */}
        <div className="glass-card sidebar-card summary-card">
          <h4 className="sidebar-card-title">Session State</h4>
          <div className="state-details">
            <div className="state-item">
              <span className="state-label">Conversation Stage:</span>
              <span className="badge badge-warning stage-badge">{conversationStage}</span>
            </div>
            <div className="state-item">
              <span className="state-label">Customer Mood:</span>
              <span className="mood-val">{decisionState.customer_mood}</span>
            </div>
            <div className="state-item">
              <span className="state-label">Suggested Action:</span>
              <p className="suggested-action-text">{decisionState.recommended_action}</p>
            </div>
          </div>
        </div>

        {/* Evaluation Metrics Card */}
        <div className="glass-card sidebar-card evaluation-card">
          <h4 className="sidebar-card-title">Live Evaluation scorecard</h4>
          <div className="metrics-list">
            {[
              { label: "Communication", key: "communication" },
              { label: "Product Knowledge", key: "product_knowledge" },
              { label: "Needs Analysis", key: "needs_analysis" },
              { label: "Pricing Accuracy", key: "pricing_accuracy" },
              { label: "Professionalism", key: "professionalism" }
            ].map((metric) => {
              const score = evaluation[metric.key];
              return (
                <div key={metric.key} className="metric-item">
                  <div className="metric-header">
                    <span>{metric.label}</span>
                    <strong>{score > 0 ? `${score}%` : "Not evaluated"}</strong>
                  </div>
                  <div className="progress-bar-container">
                    <div 
                      className="progress-bar-fill" 
                      style={{ width: `${score}%`, backgroundColor: score >= 80 ? "var(--color-success)" : score >= 50 ? "var(--color-primary)" : "var(--border-solid)" }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .chat-layout {
          display: grid;
          grid-template-columns: 280px 1fr 300px;
          gap: 20px;
          color: var(--text-primary);
        }
        .chat-main-view {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .active-vehicle-bar {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-solid);
          border-radius: var(--radius-sm);
          padding: 8px 16px;
          font-size: 0.9rem;
          color: var(--text-secondary);
        }
        .chat-sidebar {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        .sidebar-card {
          padding: 20px;
          background-color: var(--bg-surface);
          border: 1px solid var(--border-solid);
          border-radius: var(--radius-md);
        }
        .profile-title {
          font-size: 1.3rem;
          color: #FFFFFF;
          margin-bottom: 12px;
        }
        .profile-details {
          display: flex;
          flex-direction: column;
          gap: 12px;
          font-size: 0.85rem;
        }
        .detail-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .detail-label {
          color: var(--text-muted);
          font-weight: 500;
        }
        .detail-val {
          color: var(--text-primary);
        }
        .profile-list-section strong {
          color: var(--text-muted);
          display: block;
          margin-bottom: 6px;
        }
        .profile-list-section ul {
          list-style: none;
          padding-left: 0;
        }
        .profile-list-section li {
          position: relative;
          padding-left: 10px;
          margin-bottom: 4px;
          color: var(--text-secondary);
        }
        .profile-list-section li::before {
          content: "-";
          position: absolute;
          left: 0;
          color: var(--color-secondary);
        }
        .sidebar-card-title {
          font-size: 0.85rem;
          color: var(--text-muted);
          margin-bottom: 16px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          border-bottom: 1px solid var(--border-solid);
          padding-bottom: 6px;
        }
        .state-details {
          display: flex;
          flex-direction: column;
          gap: 14px;
          font-size: 0.88rem;
        }
        .state-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .state-label {
          color: var(--text-muted);
        }
        .stage-badge {
          align-self: flex-start;
          font-size: 0.75rem;
        }
        .mood-val {
          color: #FFFFFF;
          font-weight: 600;
          text-transform: capitalize;
        }
        .suggested-action-text {
          color: var(--text-secondary);
          line-height: 1.4;
          font-size: 0.85rem;
        }
        .metrics-list {
          display: flex;
          flex-direction: column;
          gap: 14px;
          font-size: 0.85rem;
        }
        .metric-item {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .metric-header {
          display: flex;
          justify-content: space-between;
          color: var(--text-secondary);
        }
        .progress-bar-container {
          height: 6px;
          background-color: var(--border-solid);
          border-radius: 3px;
          overflow: hidden;
        }
        .progress-bar-fill {
          height: 100%;
          border-radius: 3px;
          transition: width 0.3s ease;
        }
        .chat-empty-setup {
          max-width: 600px;
          margin: 0 auto;
          text-align: center;
          padding: 40px;
          background-color: var(--bg-surface);
          border: 1px solid var(--border-solid);
          border-radius: var(--radius-md);
        }
        .loading-state {
          padding: 60px;
          text-align: center;
          color: var(--text-secondary);
        }
      ` }} />
    </div>
  );
}

export default ChatPage;
