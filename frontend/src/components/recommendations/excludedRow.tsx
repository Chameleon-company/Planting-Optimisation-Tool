import React from "react";
import { ExcludedSpecies } from "@/hooks/useRecommendations";
import { renderReason } from "@/utils/recommendationHelpers";

interface ExcludedRowProps {
  item: ExcludedSpecies;
  isExpanded: boolean;
  onToggle: () => void;
}

export default function ExcludedRow({
  item,
  isExpanded,
  onToggle,
}: ExcludedRowProps) {
  return (
    <React.Fragment>
      <tr className="rec-row">
        <td className="rec-td">
          <div className="rec-primary-name">{item.species_common_name}</div>
          <div className="rec-secondary-name">{item.species_name}</div>
        </td>
        <td className="rec-td">
          <button
            className="rec-details-btn"
            onClick={onToggle}
            aria-expanded={isExpanded}
          >
            {isExpanded ? "Hide" : "Details"}
          </button>
        </td>
      </tr>
      {isExpanded && (
        <tr className="rec-expanded-row">
          <td colSpan={2}>
            <div className="rec-reason-container">
              <div className="rec-reason-header">KEY FACTORS</div>
              <div className="rec-reason-wrapper">
                <div className="rec-reason-list">
                  {item.reasons.map((reason, i) => (
                    <div key={i} className="rec-reason-item">
                      {renderReason(reason)}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </td>
        </tr>
      )}
    </React.Fragment>
  );
}
