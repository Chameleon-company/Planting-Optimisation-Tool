import { useRef } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { useGlobalWeightRuns } from "@/hooks/useGlobalWeightRuns";
import { useEpiScoring } from "@/hooks/useEpiScoring";
import GlobalWeightRunTable from "@/components/globalWeights/GlobalWeightRunTable";
import GlobalWeightsHeader from "@/components/globalWeights/GlobalWeightsHeader";

export default function GlobalWeightsPage() {
  const { runs, isLoading, error, uploadCsv, fetchRunDetails, deleteRun } =
    useGlobalWeightRuns();
  const { processEpiCsv, isEpiLoading, epiError } = useEpiScoring();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const epiFileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadCsv(e.target.files[0]);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleEpiFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processEpiCsv(e.target.files[0]);
      if (epiFileInputRef.current) epiFileInputRef.current.value = "";
    }
  };

  return (
    <div className="ahp-view-container">
      <Helmet>
        <title>Global Weights | Planting Optimisation Tool</title>
      </Helmet>

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

      {/* EPI processing section */}
      <div
        className="ahp-controls"
        style={{
          marginBottom: epiError ? "16px" : "24px",
          padding: "20px",
          backgroundColor: "#f8fafc",
          border: "1px solid #e2e8f0",
          borderRadius: "8px",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "20px",
            flexWrap: "wrap",
            width: "100%",
          }}
        >
          {/* Text column */}
          <div style={{ flex: 1, minWidth: "300px" }}>
            <h3 style={{ margin: 0, marginBottom: "15px", fontSize: "1.2rem" }}>
              EPI Data Processor
            </h3>
            <p style={{ margin: 0, color: "#64748b", fontSize: "0.95rem" }}>
              Upload a CSV containing{" "}
              <code
                style={{
                  backgroundColor: "#e2e8f0",
                  padding: "2px 6px",
                  borderRadius: "4px",
                }}
              >
                farm_id
              </code>
              ,{" "}
              <code
                style={{
                  backgroundColor: "#e2e8f0",
                  padding: "2px 6px",
                  borderRadius: "4px",
                }}
              >
                species_id
              </code>
              , and{" "}
              <code
                style={{
                  backgroundColor: "#e2e8f0",
                  padding: "2px 6px",
                  borderRadius: "4px",
                }}
              >
                farm_mean_epi
              </code>{" "}
              to automatically generate and download an enriched file containing
              raw feature scores that can be used offline to generate the Global
              Weights CSV.
            </p>
          </div>

          {/* Button column */}
          <div
            className="ahp-input-group"
            style={{ marginBottom: 0, flexShrink: 0 }}
          >
            <input
              type="file"
              accept=".csv"
              ref={epiFileInputRef}
              onChange={handleEpiFileChange}
              style={{ display: "none" }}
              id="epi-csv-upload"
            />
            <label
              htmlFor="epi-csv-upload"
              className="ahp-primary-btn"
              style={{
                margin: 0,
                textAlign: "center",
                display: "inline-block",
                backgroundColor: "#10b981",
                borderColor: "#10b981",
              }}
            >
              {isEpiLoading ? "Processing & Downloading..." : "Process EPI CSV"}
            </label>
          </div>
        </div>
      </div>

      {epiError && (
        <div className="ahp-error-message" style={{ marginBottom: "24px" }}>
          <strong>EPI Processing Error:</strong>
          <ul style={{ margin: "5px 0 0 20px", padding: 0 }}>
            {epiError.split(" | ").map((msg, idx) => (
              <li key={idx}>{msg}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Upload Controls for Global Weights */}
      <div className="ahp-controls">
        <div className="ahp-input-group">
          <h3 style={{ margin: 0, marginBottom: "15px", fontSize: "1.2rem" }}>
            Upload Global Weights (CSV)
          </h3>
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
    </div>
  );
}
