// AdminSettings.tsx
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";

function AdminSettings() {
  return (
    <>
      <Helmet>
        <title>Admin Settings | Planting Optimisation Tool</title>
      </Helmet>

      <section className="admin-page-content">
        <h2>System Settings</h2>
        <p>
          Configure scoring parameters, weighting engines, and system rules.
        </p>

        {/* The Grid Container for your Cards */}
        <div className="settings-grid">
          {/* Weighting Methods Card */}
          <Link to="/admin/settings/weighting" className="settings-card">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#f59e0b"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="settings-card-icon"
              width="32"
              height="32"
            >
              <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z" />
              <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z" />
              <path d="M7 21h10" />
              <path d="M12 3v18" />
              <path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2" />
            </svg>
            <div className="settings-card-text">
              <h3>Weighting Methods</h3>
              <p>
                Configure traditional AHP matrices or advanced ML hybrid
                scoring.
              </p>
            </div>
          </Link>

          {/* Placeholder for Scoring Parameters */}
          <Link to="/admin/settings/scoring" className="settings-card">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#3b82f6"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="settings-card-icon"
              width="32"
              height="32"
            >
              <line x1="4" y1="21" x2="4" y2="14" />
              <line x1="4" y1="10" x2="4" y2="3" />
              <line x1="12" y1="21" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12" y2="3" />
              <line x1="20" y1="21" x2="20" y2="16" />
              <line x1="20" y1="12" x2="20" y2="3" />
              <line x1="1" y1="14" x2="7" y2="14" />
              <line x1="9" y1="8" x2="15" y2="8" />
              <line x1="17" y1="16" x2="23" y2="16" />
            </svg>
            <div className="settings-card-text">
              <h3>Scoring Parameters</h3>
              <p>Adjust baseline parameters and suitability thresholds.</p>
            </div>
          </Link>

          {/* Placeholder for Exclusion Rules */}
          <Link to="/admin/settings/exclusions" className="settings-card">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#ef4444"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="settings-card-icon"
              width="32"
              height="32"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
            </svg>
            <div className="settings-card-text">
              <h3>Exclusion Rules</h3>
              <p>Manage hard constraints.</p>
            </div>
          </Link>
          {/* Placeholder for Dependency Rules */}
          <Link to="/admin/settings/dependencies" className="settings-card">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#8b5cf6"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="settings-card-icon"
              width="32"
              height="32"
            >
              <circle cx="18" cy="5" r="3" />
              <circle cx="6" cy="12" r="3" />
              <circle cx="18" cy="19" r="3" />
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
            </svg>
            <div className="settings-card-icon"></div>
            <div className="settings-card-text">
              <h3>Dependency Rules</h3>
              <p>Manage species biological dependencies.</p>
            </div>
          </Link>
        </div>
      </section>
    </>
  );
}

export default AdminSettings;
