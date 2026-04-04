
import { useState } from "react";
import { ExcludedSpecies } from "../../hooks/useRecommendations";
import { styles } from "../../utils/recommend_styles";
import { getEmptyStateStyle, getEmptyStateIcon } from "../../utils/recommendationHelpers";
import ExcludedRow from "./excludedRow";

interface ExcludedTableProps {
    data: ExcludedSpecies[];
}

export default function ExcludedTable({ data }: ExcludedTableProps) {
    const [expandedRows, setExpandedRows] = useState<number[]>([]);

    const toggleSingleRow = (id: number) => {
        setExpandedRows(prev =>
            prev.includes(id) ? prev.filter(rowId => rowId !== id) : [...prev, id]
        );
    };

    const toggleAll = () => {
        if (expandedRows.length === data.length) {
            setExpandedRows([]);
        } else {
            setExpandedRows(data.map(item => item.id));
        }
    };

    return (
        <div style={{ ...styles.resultsCard, flex: '1 1 300px', margin: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Excluded Species</h3>
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
                <div style={getEmptyStateStyle('exc')}>
                    <span style={{ fontSize: '1.2rem' }}>{getEmptyStateIcon('exc')}</span>
                    <span>No species were excluded for this farm.</span>
                </div>
            ) : (
                <table style={styles.table}>
                    <thead>
                        <tr style={styles.tableHeader}>
                            <th style={styles.th}>Species</th>
                            <th style={styles.th}>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map(item => (
                            <ExcludedRow
                                key={item.id}
                                item={item}
                                isExpanded={expandedRows.includes(item.id)}
                                onToggle={() => toggleSingleRow(item.id)}
                            />
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}