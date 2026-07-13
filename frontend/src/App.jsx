// Purpose: Top-level route configuration for core application pages.
import { NavLink, Route, Routes } from "react-router-dom";

import ChatPage from "./pages/ChatPage";
import Home from "./pages/Home";
import ReportsPage from "./pages/ReportsPage";

function App() {
  const getNavLinkClass = ({ isActive }) => {
    return `nav-link ${isActive ? "active" : ""}`;
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-logo">
          <span className="logo-icon">🚗</span>
          <span className="logo-text">AI Car Sales Coach</span>
        </div>
        <nav className="header-nav">
          <NavLink to="/" className={getNavLinkClass}>
            Dashboard
          </NavLink>
          <NavLink to="/chat" className={getNavLinkClass}>
            Training Chat
          </NavLink>
          <NavLink to="/reports" className={getNavLinkClass}>
            Coaching Reports
          </NavLink>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/reports" element={<ReportsPage />} />
        </Routes>
      </main>

      <footer className="app-footer">
        <p>© 2026 AI Car Sales Training Simulator • Clean Flat Architecture</p>
      </footer>

      {/* Embedded Component Specific CSS rules */}
      <style dangerouslySetInnerHTML={{ __html: `
        .app-container {
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }
        .app-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 40px;
          background: #1E293B;
          border-bottom: 1px solid var(--border-solid);
          position: sticky;
          top: 0;
          z-index: 100;
        }
        .header-logo {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .logo-icon {
          font-size: 1.4rem;
        }
        .logo-text {
          font-weight: 800;
          font-size: 1.15rem;
          color: #FFFFFF;
        }
        .header-nav {
          display: flex;
          gap: 16px;
        }
        .nav-link {
          color: var(--text-secondary);
          text-decoration: none;
          font-weight: 500;
          font-size: 0.95rem;
          padding: 8px 16px;
          border-radius: var(--radius-sm);
          transition: background-color 0.2s ease;
        }
        .nav-link:hover {
          color: #FFFFFF;
          background-color: #334155;
        }
        .nav-link.active {
          color: #FFFFFF;
          background-color: var(--color-primary);
          font-weight: 600;
        }
        .app-main {
          flex: 1;
          padding: 30px;
          max-width: 1300px;
          margin: 0 auto;
          width: 100%;
        }
        .app-footer {
          padding: 24px;
          text-align: center;
          border-top: 1px solid var(--border-solid);
          background-color: #1E293B;
        }
        .app-footer p {
          font-size: 0.85rem;
          color: var(--text-muted);
        }
      ` }} />
    </div>
  );
}

export default App;
