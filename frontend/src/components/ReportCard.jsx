// Purpose: Clean, flat container to render session evaluation results and feedback.
import React from "react";

function ReportCard({ report }) {
  if (!report) {
    return <div className="no-report-view">No evaluation report loaded.</div>;
  }

  const { score, summary, breakdown, recommendations } = report;

  return (
    <div className="report-card glass-card">
      <div className="report-score-section">
        <div className="score-box">
          <span className="score-num">{score}</span>
          <span className="score-max">/100</span>
        </div>
        <div className="report-summary-box">
          <h3>Overall Score</h3>
          <p>{summary || "Session performance summary is empty."}</p>
        </div>
      </div>

      {breakdown && Object.keys(breakdown).length > 0 && (
        <div className="report-breakdown-section">
          <h4>Category Breakdown</h4>
          <div className="breakdown-list">
            {Object.entries(breakdown).map(([name, val]) => (
              <div key={name} className="breakdown-item">
                <div className="breakdown-item-header">
                  <span className="breakdown-name">{name.replace(/_/g, " ")}</span>
                  <span className="breakdown-val">{val}%</span>
                </div>
                <div className="progress-bar-container">
                  <div 
                    className="progress-bar-fill" 
                    style={{ width: `${val}%`, backgroundColor: "var(--color-primary)" }} 
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {recommendations && recommendations.length > 0 && (
        <div className="report-recs-section">
          <h4>Recommendations</h4>
          <ul>
            {recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        .report-card {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-solid);
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        .report-score-section {
          display: flex;
          align-items: center;
          gap: 20px;
        }
        .score-box {
          width: 80px;
          height: 80px;
          border-radius: var(--radius-md);
          border: 2px solid var(--border-solid);
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: rgba(0, 0, 0, 0.15);
          font-weight: 800;
        }
        .score-num {
          font-size: 1.8rem;
          color: #FFFFFF;
        }
        .score-max {
          font-size: 0.8rem;
          color: var(--text-muted);
          margin-top: 8px;
        }
        .report-summary-box h3 {
          font-size: 1.1rem;
          margin-bottom: 4px;
        }
        .report-summary-box p {
          font-size: 0.9rem;
          color: var(--text-secondary);
        }
        .report-breakdown-section h4, .report-recs-section h4 {
          font-size: 0.95rem;
          color: #FFFFFF;
          margin-bottom: 12px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .breakdown-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .breakdown-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .breakdown-item-header {
          display: flex;
          justify-content: space-between;
          font-size: 0.85rem;
          font-weight: 500;
        }
        .breakdown-name {
          color: var(--text-secondary);
          text-transform: capitalize;
        }
        .breakdown-val {
          color: var(--color-secondary);
        }
        .progress-bar-container {
          height: 6px;
          background-color: rgba(255, 255, 255, 0.05);
          border-radius: var(--radius-sm);
          overflow: hidden;
        }
        .progress-bar-fill {
          height: 100%;
          border-radius: var(--radius-sm);
        }
        .report-recs-section ul {
          list-style: none;
          padding-left: 0;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .report-recs-section li {
          font-size: 0.85rem;
          color: var(--text-secondary);
          position: relative;
          padding-left: 12px;
        }
        .report-recs-section li::before {
          content: "-";
          position: absolute;
          left: 0;
          color: var(--color-primary);
        }
        .no-report-view {
          padding: 40px;
          text-align: center;
          color: var(--text-muted);
        }
      ` }} />
    </div>
  );
}

export default ReportCard;
