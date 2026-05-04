import { AhpResponse } from "@/utils/ahp_types";

interface ResultsProps {
  data: AhpResponse;
  speciesName: string;
  onReset: () => void;
  onRetry: () => void;
}

export default function AhpResultsTable({
  data,
  speciesName,
  onReset,
  onRetry,
}: ResultsProps) {
  const { weights, consistency_ratio, is_consistent } = data;
  const crPercent = (consistency_ratio * 100).toFixed(2);

  return (
    <div className="ahp-results-card">
      <h2>Results for {speciesName}</h2>

      <div className={is_consistent ? "ahp-badge-pass" : "ahp-badge-fail"}>
        Consistency Ratio: {crPercent}%
        {is_consistent ? " (Acceptable)" : " (Inconsistent - Please Retry)"}
      </div>

      <table className="ahp-table">
        <thead>
          <tr>
            <th className="ahp-th">Factor</th>
            <th className="ahp-th">Weight</th>
            <th className="ahp-th">% Importance</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(weights).map(([factor, weight]) => (
            <tr key={factor} className="ahp-tr">
              <td className="ahp-td">{factor}</td>
              <td className="ahp-td">{weight.toFixed(4)}</td>
              <td className="ahp-td">
                <div className="ahp-bar-container">
                  <div className="ahp-progress-bar-bg">
                    <div
                      className="ahp-progress-bar-fill"
                      style={{ width: `${weight * 100}%` }}
                    ></div>
                  </div>
                  <span>{(weight * 100).toFixed(1)}%</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {is_consistent ? (
        <button className="ahp-primary-btn" onClick={onReset}>
          Profile Another Species
        </button>
      ) : (
        <button className="ahp-primary-btn" onClick={onRetry}>
          Profile Again
        </button>
      )}
    </div>
  );
}
