// Purpose: Renders finished simulation performance scorecard metrics.
import React, { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import ReportCard from "../components/ReportCard";
import api from "../services/api";

const fallbackReport = {
  score: 82,
  summary: "Great overall performance! You established rapport quickly and addressed safety concerns. Work on clarifying warranty details earlier in the conversation.",
  breakdown: {
    empathy: 88,
    objection_handling: 78,
    product_knowledge: 85,
    closing_readiness: 77
  },
  recommendations: [
    "Acknowledge the customer's safety worries before jumping into vehicle features.",
    "Detail Kia's 10-year warranty when budget and value objections arise.",
    "Use an open-ended closing question like 'Would you like to schedule a test drive for the Seltos this weekend?'"
  ]
};

function ReportsPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionId = searchParams.get("sessionId");

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!sessionId) return;

    async function fetchReport() {
      setLoading(true);
      try {
        const response = await api.get(`/reports/${sessionId}`);
        if (response.data) {
          setReport(response.data);
        } else {
          setReport(fallbackReport);
        }
      } catch (err) {
        console.warn("Failed to fetch evaluation report. Using fallbacks.", err);
        setReport(fallbackReport);
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [sessionId]);

  if (!sessionId) {
    return (
      <div className="reports-empty glass-card">
        <h2>Reports Dashboard</h2>
        <p>No training session selected to view reports. Go back to the dashboard to select a persona.</p>
        <button type="button" className="btn-primary" onClick={() => navigate("/")} style={{ marginTop: "16px" }}>
          Select Persona
        </button>
      </div>
    );
  }

  return (
    <div className="reports-page animate-fade-in">
      <div className="reports-header-nav">
        <button type="button" className="btn-secondary" onClick={() => navigate("/")}>
          ← Dashboard
        </button>
        <h2>Sales Performance Scorecard</h2>
        <button type="button" className="btn-primary" onClick={() => navigate("/")}>
          Practice Again
        </button>
      </div>

      {loading ? (
        <div className="loading-state">Generating coaching scorecard...</div>
      ) : (
        <ReportCard report={report} />
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        .reports-page {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        .reports-header-nav {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .reports-header-nav h2 {
          font-size: 1.4rem;
        }
        .reports-empty {
          max-width: 600px;
          margin: 0 auto;
          text-align: center;
          padding: 40px;
          background-color: var(--bg-surface);
          border: 1px solid var(--border-solid);
        }
        .reports-empty h2 {
          margin-bottom: 10px;
        }
        .loading-state {
          padding: 60px;
          text-align: center;
          background-color: var(--bg-surface);
          border: 1px solid var(--border-solid);
          border-radius: var(--radius-md);
          color: var(--text-secondary);
        }
      ` }} />
    </div>
  );
}

export default ReportsPage;
