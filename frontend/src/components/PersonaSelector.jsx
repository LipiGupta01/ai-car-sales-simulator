// Purpose: Renders list cards for available customer personas.
import React, { useEffect, useState } from "react";
import api from "../services/api";

const fallbackPersonas = [
  {
    key: "persona-family-buyer",
    name: "Sarah & Mike Jenkins",
    persona_type: "family",
    budget_range: "$35,000 - $45,000",
    personality: "Practical, safety-first, family-focused",
    preferences: ["Spacious cabin", "Top crash safety ratings", "Warranty coverage"]
  },
  {
    key: "persona-budget-buyer",
    name: "Alex Thompson",
    persona_type: "budget",
    budget_range: "$18,000 - $25,000",
    personality: "Cautious, price-sensitive, researched",
    preferences: ["Lowest possible MSRP", "High fuel efficiency", "Bluetooth standard"]
  },
  {
    key: "persona-performance-enthusiast",
    name: "Marcus Vance",
    persona_type: "performance",
    budget_range: "$40,000 - $55,000",
    personality: "Enthusiastic, demanding, specs-driven",
    preferences: ["Turbo engine", "Paddle shifters", "Sport suspension"]
  },
  {
    key: "persona-eco-conscious-buyer",
    name: "Elena Rostova",
    persona_type: "eco",
    budget_range: "$30,000 - $40,000",
    personality: "Eco-conscious, quiet, analytical",
    preferences: ["EV/Hybrid", "Regenerative braking", "Eco materials"]
  }
];

function PersonaSelector({ onSelect }) {
  const [personas, setPersonas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPersonas() {
      try {
        const response = await api.get("/personas");
        if (response.data && response.data.length > 0) {
          setPersonas(response.data);
        } else {
          setPersonas(fallbackPersonas);
        }
      } catch (err) {
        console.warn("Failed to fetch personas. Using fallbacks.", err);
        setPersonas(fallbackPersonas);
      } finally {
        setLoading(false);
      }
    }
    fetchPersonas();
  }, []);

  if (loading) {
    return <div className="loading-state">Loading customer personas...</div>;
  }

  return (
    <div className="persona-selector">
      <h2 className="section-title">Select Customer Persona</h2>
      <div className="persona-grid">
        {personas.map((persona) => (
          <div key={persona.key || persona.id} className="glass-card persona-card">
            <div className="persona-card-header">
              <span className="persona-badge">{persona.persona_type || "standard"}</span>
              <h3 className="persona-name">{persona.name}</h3>
            </div>
            <div className="persona-card-body">
              <p className="persona-desc"><strong>Personality:</strong> {persona.personality}</p>
              <p className="persona-desc"><strong>Budget:</strong> {persona.budget_range}</p>
              <div className="persona-prefs">
                <strong>Preferences:</strong>
                <ul>
                  {persona.preferences?.slice(0, 3).map((pref, idx) => (
                    <li key={idx}>{pref}</li>
                  ))}
                </ul>
              </div>
            </div>
            <button 
              type="button" 
              className="btn-primary select-btn"
              onClick={() => onSelect(persona)}
            >
              Start Session
            </button>
          </div>
        ))}
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .persona-selector {
          margin-top: 10px;
        }
        .section-title {
          font-size: 1.4rem;
          margin-bottom: 20px;
        }
        .persona-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 20px;
        }
        .persona-card {
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          background-color: var(--bg-surface);
          border: 1px solid var(--border-solid);
        }
        .persona-card-header {
          margin-bottom: 12px;
        }
        .persona-badge {
          display: inline-block;
          font-size: 0.7rem;
          font-weight: 700;
          text-transform: uppercase;
          color: var(--color-secondary);
          margin-bottom: 4px;
        }
        .persona-name {
          font-size: 1.15rem;
          color: #FFFFFF;
        }
        .persona-card-body {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 16px;
          font-size: 0.85rem;
        }
        .persona-desc {
          color: var(--text-secondary);
        }
        .persona-prefs ul {
          margin-top: 4px;
          list-style: none;
          padding-left: 0;
        }
        .persona-prefs li {
          color: var(--text-secondary);
          position: relative;
          padding-left: 10px;
          margin-bottom: 2px;
        }
        .persona-prefs li::before {
          content: "-";
          position: absolute;
          left: 0;
          color: var(--color-primary);
        }
        .select-btn {
          width: 100%;
          border-radius: var(--radius-sm);
        }
        .loading-state {
          padding: 30px;
          text-align: center;
          color: var(--text-muted);
        }
      ` }} />
    </div>
  );
}

export default PersonaSelector;
