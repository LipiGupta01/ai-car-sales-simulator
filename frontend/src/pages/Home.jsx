import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
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
    pain_points: ["Being pressured on add-ons"]
  },
  {
    key: "persona-budget-buyer",
    name: "Alex Thompson",
    persona_type: "budget",
    budget_range: "$18,000 - $25,000",
    personality: "Cautious, price-sensitive, researched",
    preferences: ["Lowest possible MSRP", "High fuel efficiency", "Bluetooth standard"],
    goals: ["Affordable commuter", "Low financing cost"],
    pain_points: ["Hidden fees, extra features"]
  },
  {
    key: "persona-performance-enthusiast",
    name: "Marcus Vance",
    persona_type: "performance",
    budget_range: "$40,000 - $55,000",
    personality: "Enthusiastic, demanding, specs-driven",
    preferences: ["Turbo engine", "Paddle shifters", "Sport suspension"],
    goals: ["Speed and dynamic response", "Advanced connectivity"],
    pain_points: ["Lacking power, slow transmission"]
  },
  {
    key: "persona-eco-conscious-buyer",
    name: "Elena Rostova",
    persona_type: "eco",
    budget_range: "$30,000 - $40,000",
    personality: "Eco-conscious, quiet, analytical",
    preferences: ["EV/Hybrid", "Regenerative braking", "Eco materials"],
    goals: ["Low fuel usage", "Reduced emissions"],
    pain_points: ["Lack of charge network info"]
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

function Home() {
  const navigate = useNavigate();
  const [personas, setPersonas] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [selectedPersonaKey, setSelectedPersonaKey] = useState("");
  const [selectedVehicleKey, setSelectedVehicleKey] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [personasRes, vehiclesRes] = await Promise.all([
          api.get("/personas").catch(() => ({ data: [] })),
          api.get("/vehicles").catch(() => ({ data: [] }))
        ]);

        if (personasRes.data && personasRes.data.length > 0) {
          setPersonas(personasRes.data);
        } else {
          setPersonas(fallbackPersonas);
        }

        if (vehiclesRes.data && vehiclesRes.data.length > 0) {
          setVehicles(vehiclesRes.data);
        } else {
          setVehicles(fallbackVehicles);
        }
      } catch (err) {
        console.warn("Failed to fetch data, utilizing fallbacks", err);
        setPersonas(fallbackPersonas);
        setVehicles(fallbackVehicles);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleStartSimulation = () => {
    if (selectedPersonaKey && selectedVehicleKey) {
      navigate(`/chat?personaKey=${selectedPersonaKey}&vehicleKey=${selectedVehicleKey}`);
    }
  };

  if (loading) {
    return <div className="loading-state">Loading simulation assets...</div>;
  }

  return (
    <div className="home-container">
      <div className="welcome-banner">
        <h1>AI Car Sales Training Simulator</h1>
        <p>
          Practice customer consultations, handle objections, and master vehicle product specifications in real-time. Choose a buyer profile and a practice vehicle below to launch the simulation.
        </p>
      </div>

      <div className="selection-sections">
        {/* Section 1: Persona Selection */}
        <div className="selection-section">
          <h2>1. Select Customer Persona</h2>
          <div className="grid-layout">
            {personas.map((persona) => {
              const key = persona.key || persona.id;
              const isSelected = selectedPersonaKey === key;
              return (
                <div
                  key={key}
                  className={`selection-card ${isSelected ? "selected" : ""}`}
                  onClick={() => setSelectedPersonaKey(key)}
                >
                  <div className="card-header">
                    <span className="badge badge-info">{persona.persona_type || "standard"}</span>
                    <h3>{persona.name}</h3>
                  </div>
                  <div className="card-body">
                    <p><strong>Personality:</strong> {persona.personality}</p>
                    <p><strong>Budget Range:</strong> {persona.budget_range}</p>
                    <div className="card-list">
                      <strong>Preferences:</strong>
                      <ul>
                        {persona.preferences?.slice(0, 3).map((pref, idx) => (
                          <li key={idx}>{pref}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Section 2: Vehicle Selection */}
        <div className="selection-section">
          <h2>2. Select Vehicle</h2>
          <div className="grid-layout">
            {vehicles.map((vehicle) => {
              const key = vehicle.key || vehicle.id;
              const isSelected = selectedVehicleKey === key;
              return (
                <div
                  key={key}
                  className={`selection-card ${isSelected ? "selected" : ""}`}
                  onClick={() => setSelectedVehicleKey(key)}
                >
                  <div className="card-header">
                    <span className="badge badge-success">{vehicle.category}</span>
                    <h3>{vehicle.year} {vehicle.make} {vehicle.model}</h3>
                  </div>
                  <div className="card-body">
                    <p className="vehicle-msrp">MSRP: <strong>${vehicle.msrp.toLocaleString()}</strong></p>
                    <div className="card-list">
                      <strong>Features:</strong>
                      <div className="features-container">
                        {vehicle.features?.map((feat, idx) => (
                          <span key={idx} className="feature-pill">{feat}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Section 3: Start Simulation Button */}
      <div className="action-container">
        <button
          type="button"
          className="btn-primary start-btn"
          disabled={!selectedPersonaKey || !selectedVehicleKey}
          onClick={handleStartSimulation}
        >
          Start Simulation
        </button>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .home-container {
          display: flex;
          flex-direction: column;
          gap: 40px;
          color: var(--text-primary);
        }
        .welcome-banner {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-solid);
          border-radius: var(--radius-md);
          padding: 28px;
        }
        .welcome-banner h1 {
          font-size: 2rem;
          margin-bottom: 12px;
        }
        .welcome-banner p {
          font-size: 1rem;
          color: var(--text-secondary);
          max-width: 900px;
        }
        .selection-sections {
          display: flex;
          flex-direction: column;
          gap: 36px;
        }
        .selection-section h2 {
          font-size: 1.5rem;
          margin-bottom: 18px;
          border-bottom: 2px solid var(--border-solid);
          padding-bottom: 8px;
        }
        .grid-layout {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 20px;
        }
        .selection-card {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-solid);
          border-radius: var(--radius-md);
          padding: 20px;
          cursor: pointer;
          transition: border-color 0.2s, box-shadow 0.2s;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
        }
        .selection-card:hover {
          border-color: var(--text-muted);
        }
        .selection-card.selected {
          border-color: var(--color-primary);
          box-shadow: 0 0 0 2px var(--color-primary);
        }
        .card-header {
          display: flex;
          flex-direction: column;
          gap: 6px;
          margin-bottom: 14px;
        }
        .card-header h3 {
          font-size: 1.2rem;
          color: #FFFFFF;
        }
        .card-body {
          font-size: 0.9rem;
          color: var(--text-secondary);
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .card-list ul {
          list-style: none;
          margin-top: 6px;
        }
        .card-list li {
          position: relative;
          padding-left: 12px;
          margin-bottom: 4px;
        }
        .card-list li::before {
          content: "•";
          position: absolute;
          left: 0;
          color: var(--color-primary);
        }
        .vehicle-msrp {
          font-size: 0.95rem;
        }
        .features-container {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-top: 6px;
        }
        .feature-pill {
          background-color: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--border-solid);
          border-radius: var(--radius-sm);
          padding: 2px 8px;
          font-size: 0.75rem;
          color: var(--text-secondary);
        }
        .action-container {
          display: flex;
          justify-content: center;
          margin-top: 10px;
        }
        .start-btn {
          font-size: 1.1rem;
          padding: 14px 36px;
          border-radius: var(--radius-sm);
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

export default Home;
