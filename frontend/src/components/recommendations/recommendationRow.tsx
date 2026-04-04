import React from "react";
import { Recommendation } from "../../hooks/useRecommendations";
import { styles } from "../../utils/recommend_styles";
import { renderReason, getBarColor } from "../../utils/recommendationHelpers";

interface RecommendationRowProps {
    item: Recommendation;
    isExpanded: boolean;
    onToggle: () => void;
}

export default function RecommendationRow({ item, isExpanded, onToggle }: RecommendationRowProps) {
    return (
        <React.Fragment>
            <tr style={styles.tr}>
                <td style={styles.td}>{item.rank_overall}</td>
                <td style={styles.td}>
                    <div style={styles.primaryName}>{item.species_common_name}</div>
                    <div style={styles.secondaryName}>{item.species_name}</div>
                </td>
                <td style={styles.td}>
                    <div style={styles.scoreContainer}>
                        <span style={styles.scoreValue}>{(item.score_mcda * 100).toFixed(0)}%</span>
                        <div style={styles.progressBarBg}>
                            <div style={{
                                ...styles.progressBarFill,
                                width: `${item.score_mcda * 100}%`,
                                backgroundColor: getBarColor(item.score_mcda)
                            }}></div>
                        </div>
                    </div>
                </td>
                <td style={styles.td}>
                    <button style={styles.detailsBtn} onClick={onToggle}>
                        {isExpanded ? 'Hide' : 'Details'}
                    </button>
                </td>
            </tr>

            {isExpanded && (
                <tr style={styles.expandedRow}>
                    <td colSpan={4}>
                        <div style={styles.reasonContainer}>
                            <div style={styles.reasonHeader}>KEY FACTORS</div>
                            <div style={styles.reasonWrapper}>
                                <div style={styles.reasonList}>
                                    {item.key_reasons.map((reason, i) => (
                                        <div key={i} style={styles.reasonItem}>
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