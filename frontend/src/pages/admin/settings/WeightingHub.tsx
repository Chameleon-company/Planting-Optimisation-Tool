import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";

export default function WeightingHub() {
  return (
    <>
      <Helmet>
        <title>Weighting Methods | Planting Optimisation Tool</title>
      </Helmet>

      <section className="admin-page-content">
        {/* A back button for easy navigation */}
        <div className="admin-back-nav">
          <Link to="/admin/settings" className="admin-back-link">
            ← Back to Settings
          </Link>
        </div>

        <h2>Weighting Methods</h2>
        <p>
          Select a scoring method to configure its specific parameters and
          rules.
        </p>

        <div className="settings-grid">
          {/* Standard AHP */}
          <Link to="/admin/settings/weighting/ahp" className="settings-card">
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
              <h3>Traditional AHP</h3>
              <p>
                Expert-driven pairwise comparison matrix and Eigenvector
                weighting.
              </p>
            </div>
          </Link>

          {/* Hybrid ML */}
          <Link to="/admin/settings/weighting/hybrid" className="settings-card">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#ec4899"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="settings-card-icon"
              width="32"
              height="32"
            >
              <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z" />
              <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z" />
              <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4" />
              <path d="M17.599 6.5A3 3 0 0 0 14 6" />
              <path d="M6.401 6.5A3 3 0 0 1 10 6" />
              <path d="M12 18v-5" />
            </svg>
            <div className="settings-card-text">
              <h3>Hybrid AHP/ML</h3>
              <p>
                Nuanced scoring engine utilising machine learning models
                alongside baseline parameters.
              </p>
            </div>
          </Link>
        </div>
      </section>
    </>
  );
}
