import { useRef } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { useGlobalWeightRuns } from "@/hooks/useGlobalWeightRuns";
import GlobalWeightRunTable from "@/components/globalWeights/GlobalWeightRunTable";
import GlobalWeightsHeader from "@/components/globalWeights/GlobalWeightsHeader";

export default function GlobalWeightsPage() {
  const { runs, isLoading, error, uploadCsv, fetchRunDetails, deleteRun } =
    useGlobalWeightRuns();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadCsv(e.target.files[0]);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="ahp-view-container">
      <Helmet>
        <title>Global Weights | Planting Optimisation Tool</title>
      </Helmet>

      <section
        className="admin-page-content"
        style={{ maxWidth: "1200px", margin: "0 auto", padding: "40px 20px" }}
      >
        {/* Back Button */}
        <div style={{ marginBottom: "24px" }}>
          <Link
            to="/admin/settings/weighting"
            style={{
              textDecoration: "none",
              color: "#4f46e5",
              fontWeight: "500",
            }}
          >
            ← Back to Weighting Methods
          </Link>
        </div>

        <GlobalWeightsHeader />

        {/* Upload Controls */}
        <div className="ahp-controls">
          <div className="ahp-input-group">
            <label className="ahp-label">Upload Global Weights (CSV)</label>
            <input
              type="file"
              accept=".csv"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: "none" }}
              id="csv-upload"
            />
            <label
              htmlFor="csv-upload"
              className="ahp-primary-btn"
              style={{ textAlign: "center", display: "inline-block" }}
            >
              {isLoading ? "Processing..." : "Select & Upload CSV"}
            </label>
          </div>
        </div>

        {error && (
          <div className="ahp-error-message">
            <strong>Upload Error:</strong>
            <ul style={{ margin: "5px 0 0 20px", padding: 0 }}>
              {error.split(" | ").map((msg, idx) => (
                <li key={idx}>{msg}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Data Display */}
        <GlobalWeightRunTable
          runs={runs}
          fetchDetails={fetchRunDetails}
          deleteRun={deleteRun}
        />
      </section>
    </div>
  );
}
