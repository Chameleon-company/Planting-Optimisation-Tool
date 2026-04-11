// AdminSettings.tsx
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
// Optional: Import icons from an icon library like lucide-react or react-icons if you aren't using static images

function AdminSettings() {
  return (
    <>
      <Helmet>
        <title>Admin Settings | Planting Optimisation Tool</title>
      </Helmet>

      <section className="admin-page-content">
        <h2>System Settings</h2>
        <p>Configure scoring parameters, weighting engines, and system rules.</p>

        {/* The Grid Container for your Cards */}
        <div className="settings-grid">

          {/* Weighting Methods Card */}
          <Link to="/admin/settings/weighting" className="settings-card">
            <div className="settings-card-icon">⚖️</div>
            <div className="settings-card-text">
              <h3>Weighting Methods</h3>
              <p>Configure traditional AHP matrices or advanced ML hybrid scoring.</p>
            </div>
          </Link>

          {/* Placeholder for Scoring Parameters */}
          <Link to="/admin/settings/scoring" className="settings-card">
            <div className="settings-card-icon">
              📊
            </div>
            <div className="settings-card-text">
              <h3>Scoring Parameters</h3>
              <p>Adjust baseline parameters and suitability thresholds.</p>
            </div>
          </Link>

          {/* Placeholder for Exclusion Rules */}
          <Link to="/admin/settings/exclusions" className="settings-card">
            <div className="settings-card-icon">
              🚫
            </div>
            <div className="settings-card-text">
              <h3>Exclusion Rules</h3>
              <p>Manage hard constraints.</p>
            </div>
          </Link>
          {/* Placeholder for Dependency Rules */}
          <Link to="/admin/settings/dependencies" className="settings-card">
            <div className="settings-card-icon">

            </div>
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
