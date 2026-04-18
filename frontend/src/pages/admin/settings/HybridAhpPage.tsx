import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";

export default function HybridAhpPage() {
  return (
    <>
      <Helmet>
        <title>Hybrid AHP/ML Engine | Planting Optimisation Tool</title>
      </Helmet>

      <section className="admin-page-content">
        <div className="admin-back-nav">
          <Link to="/admin/settings/weighting" className="admin-back-link">
            ← Back to Weighting Methods
          </Link>
        </div>

        <h2>Hybrid AHP/ML Scoring Engine</h2>
        <p>
          Configure the Multi-Criteria Decision Analysis (MCDA) engine
          parameters, blending expert-driven heuristics with data-driven models.
        </p>

        <div className="admin-content-card">
          <h3>Engine Configuration Workspace</h3>
          <p style={{ color: "#64748b" }}>
            This placeholder page will later support configuration controls for
            the hybrid engine.
          </p>

          <ul className="admin-content-list">
            <li>
              <strong>Constraint Balancing:</strong> Adjust the influence of AHP
              matrices versus machine learning predictions.
            </li>
            <li>
              <strong>Constraint Balancing:</strong> Adjust the influence of AHP
              matrices versus machine learning predictions.
            </li>
          </ul>
        </div>
      </section>
    </>
  );
}
