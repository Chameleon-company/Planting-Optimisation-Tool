import { useState } from "react";
import { Recommendation } from "../../hooks/useRecommendations";
import { styles } from "../../utils/recommend_styles";
import { getEmptyStateStyle, getEmptyStateIcon } from "../../utils/recommendationHelpers";
import RecommendationRow from "./recommendationRow";

interface RecommendationTableProps {
    title: string;
    data: Recommendation[];
    emptyMessage: string;
    type: 'top' | 'caut';
}

export default function RecommendationTable({ title, data, emptyMessage, type }: RecommendationTableProps) {
    // State to track which row IDs are currently expanded
    const [expandedRows, setExpandedRows] = useState<number[]>([]);

    const toggleSingleRow = (id: number) => {
        setExpandedRows(prev =>
            prev.includes(id) ? prev.filter(rowId => rowId !== id) : [...prev, id]
        );
    };

    const toggleAll = () => {
        if (expandedRows.length === data.length) {
            setExpandedRows([]); // Collapse all
        } else {
            setExpandedRows(data.map(item => item.species_id)); // Expand all
        }
    };

    return (
        <div style={{ ...styles.resultsCard, flex: '1 1 300px', margin: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{title}</h3>

                {data.length > 0 && (
                    <button
                        style={{ ...styles.detailsBtn, width: 'auto', padding: '4px 12px' }}
                        onClick={toggleAll}
                    >
                        {expandedRows.length === data.length ? 'Collapse All' : 'Expand All'}
                    </button>
                )}
            </div>

            {data.length === 0 ? (
                <div style={getEmptyStateStyle(type)}>
                    <span style={{ fontSize: '1.2rem' }}>{getEmptyStateIcon(type)}</span>
                    <span>{emptyMessage}</span>
                </div>
            ) : (
                <table style={styles.table}>
                    <thead>
                        <tr style={styles.tableHeader}>
                            <th style={styles.th}>Rank</th>
                            <th style={styles.th}>Species</th>
                            <th style={styles.th}>Score</th>
                            <th style={styles.th}>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map(item => (
                            <RecommendationRow
                                key={item.species_id}
                                item={item}
                                isExpanded={expandedRows.includes(item.species_id)}
                                onToggle={() => toggleSingleRow(item.species_id)}
                            />
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}