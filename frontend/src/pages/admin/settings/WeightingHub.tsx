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
                <p>Select a scoring method to configure its specific parameters and rules.</p>

                <div className="settings-grid">

                    {/* Standard AHP */}
                    <Link to="/admin/settings/weighting/ahp" className="settings-card">
                        <div className="settings-card-icon">📊</div>
                        <div className="settings-card-text">
                            <h3>Traditional AHP</h3>
                            <p>Expert-driven pairwise comparison matrix and Eigenvector weighting.</p>
                        </div>
                    </Link>

                    {/* Hybrid ML */}
                    <Link to="/admin/settings/weighting/hybrid" className="settings-card">
                        <div className="settings-card-icon">🧠</div>
                        <div className="settings-card-text">
                            <h3>Hybrid AHP/ML</h3>
                            <p>Nuanced scoring engine utilising machine learning models alongside baseline parameters.</p>
                        </div>
                    </Link>

                </div>
            </section>
        </>
    );
}

