import { useState } from "react";
import {
  GlobalWeightsRunSummary,
  GlobalWeightItem,
} from "@/utils/globalWeightHelpers";
import GlobalWeightRunRow from "./GlobalWeightRunRow";
import "@/pages/recommendations.css";

interface GlobalWeightRunTableProps {
  runs: GlobalWeightsRunSummary[];
  fetchDetails: (id: string) => Promise<GlobalWeightItem[]>;
  deleteRun: (id: string) => void;
}

export default function GlobalWeightRunTable({
  runs,
  fetchDetails,
  deleteRun,
}: GlobalWeightRunTableProps) {
  const [expandedRows, setExpandedRows] = useState<string[]>([]);

  const toggleRow = (id: string) => {
    setExpandedRows(prev =>
      prev.includes(id) ? prev.filter(rowId => rowId !== id) : [...prev, id]
    );
  };

  if (runs.length === 0) {
    return (
      <div className="rec-placeholder-box" style={{ marginTop: "20px" }}>
        <span>
          No global weight runs available. Upload a CSV to get started.
        </span>
      </div>
    );
  }

  return (
    <div
      className="rec-results-card"
      style={{ marginTop: "20px", width: "100%" }}
    >
      <h3 style={{ margin: 0, marginBottom: "15px", fontSize: "1.2rem" }}>
        Global Weight Runs
      </h3>
      <table className="rec-table">
        <thead>
          <tr className="rec-thead">
            <th className="rec-th">Run ID</th>
            <th className="rec-th">Date</th>
            <th className="rec-th">Bootstraps</th>
            <th className="rec-th">Early Stopped</th>
            <th className="rec-th">Source</th>
            <th className="rec-th">Action</th>
          </tr>
        </thead>
        <tbody>
          {runs.map(run => (
            <GlobalWeightRunRow
              key={run.run_id}
              run={run}
              isExpanded={expandedRows.includes(run.run_id)}
              onToggle={() => toggleRow(run.run_id)}
              fetchDetails={fetchDetails}
              onDelete={deleteRun}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
