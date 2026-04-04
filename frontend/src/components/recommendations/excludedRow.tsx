import React from "react";
import { ExcludedSpecies } from "../../hooks/useRecommendations";
import { styles } from "../../utils/recommend_styles";
import { renderReason } from "../../utils/recommendationHelpers";

interface ExcludedRowProps {
    item: ExcludedSpecies;
    isExpanded: boolean;
    onToggle: () => void;
}

export default function ExcludedRow({ item, isExpanded, onToggle }: ExcludedRowProps) {
    return (
        <React.Fragment>
            <tr style={styles.tr}>
                <td style={styles.td}>
                    <div style={styles.primaryName}>{item.species_common_name}</div>
                    <div style={styles.secondaryName}>{item.species_name}</div>
                </td>
                <td style={styles.td}>
                    <button style={styles.detailsBtn} onClick={onToggle}>
                        {isExpanded ? 'Hide' : 'Details'}
                    </button>
                </td>
            </tr>
            {isExpanded && (
                <tr style={styles.expandedRow}>
                    <td colSpan={2}>
                        <div style={styles.reasonContainer}>
                            <div style={styles.reasonHeader}>KEY FACTORS</div>
                            <div style={styles.reasonWrapper}>
                                <div style={styles.reasonList}>
                                    {item.reasons.map((reason, i) => (
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