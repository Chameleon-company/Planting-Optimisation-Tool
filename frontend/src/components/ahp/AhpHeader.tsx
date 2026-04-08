import { styles } from '@/utils/ahp_styles';

export default function AhpHeader() {
    return (
        <div>
            <h2 style={styles.viewTitle}>Expert Weighting - Analytic Hierarchy Process (AHP)</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
                Establish MCDA factor weights via pairwise comparison.
            </p>
        </div>
    );
}