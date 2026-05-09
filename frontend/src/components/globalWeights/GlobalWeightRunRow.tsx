import React, { useState, useEffect } from "react";
import {
  GlobalWeightsRunSummary,
  GlobalWeightItem,
  interpretGlobalWeights,
  formatFactor,
} from "@/utils/globalWeightHelpers";

interface GlobalWeightRunRowProps {
  run: GlobalWeightsRunSummary;
  isExpanded: boolean;
  onToggle: () => void;
  fetchDetails: (id: string) => Promise<GlobalWeightItem[]>;
  onDelete: (id: string) => void;
}

export default function GlobalWeightRunRow({
  run,
  isExpanded,
  onToggle,
  fetchDetails,
  onDelete,
}: GlobalWeightRunRowProps) {
  const [items, setItems] = useState<GlobalWeightItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isExpanded && items.length === 0) {
      setIsLoading(true);
      fetchDetails(run.run_id)
        .then(setItems)
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [isExpanded, run.run_id]);

  const interpretation =
    items.length > 0 ? interpretGlobalWeights(items) : null;

  return (
    <React.Fragment>
      <tr>
        <td className="rec-td">
          <div
            style={{
              fontSize: "0.85rem",
              color: "#555",
              fontFamily: "monospace",
            }}
          >
            {run.run_id.split("-")[0]}...
          </div>
        </td>
        <td className="rec-td">{new Date(run.created_at).toLocaleString()}</td>
        <td className="rec-td">{run.bootstraps}</td>
        <td className="rec-td">
          {run.bootstrap_early_stopped ? (
            <span style={{ color: "#28a745", fontWeight: "bold" }}>Yes</span>
          ) : (
            <span style={{ color: "#6c757d" }}>No</span>
          )}
        </td>
        <td className="rec-td">{run.source || "System"}</td>
        <td className="rec-td">
          <div style={{ display: "flex", gap: "8px" }}>
            <button className="rec-details-btn" onClick={onToggle}>
              {isExpanded ? "Hide Details" : "View Weights"}
            </button>
            <button
              className="rec-details-btn"
              style={{ borderColor: "#dc3545", color: "#dc3545" }} // Red styling for destructive action
              onClick={() => {
                if (
                  window.confirm(
                    "Are you sure you want to delete this global weight run? This cannot be undone."
                  )
                ) {
                  onDelete(run.run_id);
                }
              }}
            >
              Delete
            </button>
          </div>
        </td>
      </tr>

      {isExpanded && (
        <tr className="rec-expanded-row">
          <td colSpan={6} style={{ padding: "20px" }}>
            {isLoading ? (
              <div style={{ textAlign: "center", padding: "20px" }}>
                Loading weights...
              </div>
            ) : (
              <div className="gw-details-container">
                {interpretation && (
                  <p
                    style={{
                      fontStyle: "italic",
                      marginBottom: "15px",
                      color: "#555",
                    }}
                  >
                    {interpretation.overview}
                  </p>
                )}
                <table
                  className="rec-table"
                  style={{ marginTop: 0, backgroundColor: "#fff" }}
                >
                  <thead>
                    <tr>
                      <th className="rec-th">Feature</th>
                      <th className="rec-th">Mean Weight</th>
                      <th className="rec-th">CI [Lower, Upper]</th>
                      <th className="rec-th">CI Width</th>
                      <th className="rec-th">Touches Zero</th>
                      <th className="rec-th">Commentary</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map(item => (
                      <tr key={item.feature}>
                        <td className="rec-td">
                          <strong>{formatFactor(item.feature)}</strong>
                        </td>
                        <td className="rec-td">
                          {item.mean_weight.toFixed(3)}
                        </td>
                        <td className="rec-td">
                          [{item.ci_lower.toFixed(3)},{" "}
                          {item.ci_upper.toFixed(3)}]
                        </td>
                        <td className="rec-td">{item.ci_width.toFixed(3)}</td>
                        <td className="rec-td">
                          {item.touches_zero ? (
                            <span style={{ color: "#dc3545" }}>Yes</span>
                          ) : (
                            <span style={{ color: "#28a745" }}>No</span>
                          )}
                        </td>
                        <td
                          className="rec-td"
                          style={{
                            maxWidth: "300px",
                            fontSize: "0.85rem",
                            color: "#444",
                            lineHeight: "1.4",
                          }}
                        >
                          {interpretation?.commentary[item.feature]}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </td>
        </tr>
      )}
    </React.Fragment>
  );
}
