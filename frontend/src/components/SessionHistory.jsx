// Purpose: Renders a history log of recent training sessions and their evaluation grades.
import { useEffect, useState } from "react";
import api from "../services/api";

function SessionHistory({ onSelectSession, activeSessionId }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const response = await api.get("/sessions");
        if (response.data) {
          setSessions(response.data);
        }
      } catch (err) {
        console.warn("Failed to retrieve sessions list from backend.", err);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, [activeSessionId]);

  if (loading) {
    return <div className="loading-state">Loading training logs...</div>;
  }

  const formatDate = (isoString) => {
    if (!isoString) return "";
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    } catch {
      return "";
    }
  };

  const formatPersonaName = (personaId) => {
    if (personaId.includes("buyer")) return "Alex Thompson";
    if (personaId.includes("family")) return "Priya Nair";
    return personaId;
  };

  return (
    <section className="history-section">
      <h3 className="history-title">Session Log History</h3>
      {sessions.length === 0 ? (
        <p className="no-history-text">No previous session logs found. Select a persona above to begin practice.</p>
      ) : (
        <div className="history-list">
          {sessions.map((sess) => {
            const isCurrent = sess.external_id === activeSessionId;
            return (
              <div 
                key={sess.external_id} 
                className={`history-item ${isCurrent ? "history-item-current" : ""}`}
                onClick={() => onSelectSession(sess)}
              >
                <div className="history-item-left">
                  <span className="history-avatar-icon">📋</span>
                  <div>
                    <span className="history-persona">{formatPersonaName(sess.persona_id)}</span>
                    <span className="history-date">{formatDate(sess.created_at)}</span>
                  </div>
                </div>

                <div className="history-item-right">
                  {sess.status === "evaluated" ? (
                    <span className="badge badge-success">Graded</span>
                  ) : (
                    <span className="badge badge-warning">Active</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        .history-section {
          margin-top: 30px;
        }
        .history-title {
          font-size: 1.15rem;
          color: white;
          margin-bottom: 12px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .no-history-text {
          font-size: 0.9rem;
          color: var(--text-muted);
        }
        .history-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .history-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid var(--border-glass);
          border-radius: var(--radius-md);
          padding: 12px 18px;
          cursor: pointer;
          transition: var(--transition-smooth);
        }
        .history-item:hover {
          background: rgba(255, 255, 255, 0.05);
          border-color: var(--border-glass-hover);
        }
        .history-item-current {
          background: rgba(139, 92, 246, 0.05);
          border-color: rgba(139, 92, 246, 0.3);
        }
        .history-item-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .history-avatar-icon {
          font-size: 1.25rem;
          background: rgba(255, 255, 255, 0.04);
          width: 32px;
          height: 32px;
          border-radius: var(--radius-sm);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .history-persona {
          font-size: 0.95rem;
          font-weight: 600;
          color: white;
          display: block;
        }
        .history-date {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
      ` }} />
    </section>
  );
}

export default SessionHistory;
