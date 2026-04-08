import { AhpResponse } from '@/utils/ahp_types';
import { styles } from '@/utils/ahp_styles';

interface ResultsProps {
    data: AhpResponse;
    speciesName: string;
    onReset: () => void;
    onRetry: () => void;
}

export default function AhpResultsTable({ data, speciesName, onReset, onRetry }: ResultsProps) {
    const { weights, consistency_ratio, is_consistent } = data;
    const crPercent = (consistency_ratio * 100).toFixed(2);

    return (
        <div style={styles.resultsCard}>
            <h2>Results for {speciesName}</h2>

            <div style={is_consistent ? styles.badgePass : styles.badgeFail}>
                Consistency Ratio: {crPercent}%
                {is_consistent ? " (Acceptable)" : " (Inconsistent - Please Retry)"}
            </div>

            <table style={styles.table}>
                <thead>
                    <tr>
                        <th style={styles.th}>Factor</th>
                        <th style={styles.th}>Weight</th>
                        <th style={styles.th}>% Importance</th>
                    </tr>
                </thead>
                <tbody>
                    {Object.entries(weights).map(([factor, weight]) => (
                        <tr key={factor} style={styles.tr}>
                            <td style={styles.td}>{factor}</td>
                            <td style={styles.td}>{weight.toFixed(4)}</td>
                            <td style={styles.td}>
                                <div style={styles.barContainer}>
                                    <div style={styles.progressBarBg}>
                                        <div style={{ ...styles.progressBarFill, width: `${weight * 100}%` }}></div>
                                    </div>
                                    <span>{(weight * 100).toFixed(1)}%</span>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {is_consistent ? (
                <button style={styles.primaryBtn} onClick={onReset}>
                    Profile Another Species
                </button>
            ) : (
                <button style={styles.primaryBtn} onClick={onRetry}>
                    Profile Again
                </button>
            )}
        </div>
    );
}