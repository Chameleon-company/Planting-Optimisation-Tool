import React from "react";
import { Recommendation } from "@/hooks/useRecommendations";
import "@/pages/recommendations.css";
import { renderReason, getBarColor } from "@/utils/recommendationHelpers";

interface RecommendationRowProps {
  item: Recommendation;
  isExpanded: boolean;
  onToggle: () => void;
}

export default function RecommendationRow({
  item,
  isExpanded,
  onToggle,
}: RecommendationRowProps) {
  return (
    <React.Fragment>
      <tr>
        <td className="rec-td">{item.rank_overall}</td>
        <td className="rec-td">
          <div className="rec-primary-name">{item.species_common_name}</div>
          <div className="rec-secondary-name">{item.species_name}</div>
        </td>
        <td className="rec-td">
          <div className="rec-score-container">
            <span className="rec-score-value">
              {(item.score_mcda * 100).toFixed(0)}%
            </span>
            <div className="rec-progress-bar-bg">
              <div
                className="rec-progress-bar-fill"
                style={{
                  width: `${item.score_mcda * 100}%`,
                  backgroundColor: getBarColor(item.score_mcda),
                }}
              ></div>
            </div>
          </div>
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
          <td colSpan={4}>
            <div className="rec-reason-container">
              <div className="rec-reason-header">KEY FACTORS</div>
              <div className="rec-reason-wrapper">
                <div className="rec-reason-list">
                  {item.key_reasons.map((reason, i) => (
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
