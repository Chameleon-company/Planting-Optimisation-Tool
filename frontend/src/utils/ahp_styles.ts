import React from 'react';

export const styles: Record<string, React.CSSProperties> = {
    viewContainer: { padding: '20px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'sans-serif' },
    viewTitle: { fontSize: '1.8rem', color: '#333', marginBottom: '20px' },
    controls: { display: 'flex', gap: '15px', alignItems: 'flex-end', marginBottom: '20px', backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px', border: '1px solid #e9ecef' },
    inputGroup: { display: 'flex', flexDirection: 'column', gap: '5px' },
    label: { fontSize: '0.9rem', fontWeight: 600, color: '#495057' },
    select: { padding: '10px', borderRadius: '4px', border: '1px solid #ced4da', fontSize: '1rem', minWidth: '250px', backgroundColor: '#fff' },
    resultsCard: { backgroundColor: '#fff', borderRadius: '8px', padding: '30px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', border: '1px solid #e9ecef', marginTop: '20px', textAlign: 'center' },
    primaryBtn: { backgroundColor: '#2c3e50', color: '#fff', border: 'none', padding: '12px 24px', borderRadius: '6px', cursor: 'pointer', fontSize: '1rem', fontWeight: 600, marginTop: '20px' },
    secondaryBtn: { backgroundColor: 'transparent', color: '#6c757d', border: '1px solid #ced4da', padding: '12px 24px', borderRadius: '6px', cursor: 'pointer', fontSize: '1rem', fontWeight: 600, transition: 'all 0.2s' },

    // Comparison specifics
    comparisonBox: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '30px 0', fontSize: '1.5rem', fontWeight: 'bold' },
    factorLeft: { color: '#2c3e50', flex: 1, textAlign: 'right' },
    vs: { fontSize: '1rem', color: '#95a5a6', margin: '0 20px' },
    factorRight: { color: '#27ae60', flex: 1, textAlign: 'left' },
    scaleContainer: { display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '10px', flexWrap: 'wrap' },
    scaleBtn: { width: '45px', height: '45px', border: '1px solid #ced4da', background: '#fff', cursor: 'pointer', borderRadius: '50%', fontWeight: 'bold', transition: 'all 0.2s' },

    scaleWrapper: { display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '20px', marginTop: '20px' },
    iconSide: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', minWidth: '80px' },
    svgIcon: { width: '90px', height: '90px', objectFit: 'contain' },
    iconLabel: { fontSize: '0.85rem', color: '#6c757d', fontWeight: 600 },

    // Results specifics
    badgePass: { padding: '10px', borderRadius: '6px', fontWeight: 'bold', display: 'inline-block', marginBottom: '20px', background: '#d4edda', color: '#155724' },
    badgeFail: { padding: '10px', borderRadius: '6px', fontWeight: 'bold', display: 'inline-block', marginBottom: '20px', background: '#f8d7da', color: '#721c24' },
    table: { width: '100%', borderCollapse: 'collapse', marginTop: '20px' },
    th: { borderBottom: '2px solid #dee2e6', padding: '12px', textAlign: 'left', color: '#495057', fontWeight: 600 },
    tr: { borderBottom: '1px solid #e9ecef' },
    td: { padding: '12px', textAlign: 'left' },
    barContainer: { display: 'flex', alignItems: 'center', gap: '10px' },
    progressBarBg: { backgroundColor: '#e9ecef', height: '10px', borderRadius: '5px', width: '100px', overflow: 'hidden' },
    progressBarFill: { height: '100%', borderRadius: '5px', backgroundColor: '#3498db' },

};