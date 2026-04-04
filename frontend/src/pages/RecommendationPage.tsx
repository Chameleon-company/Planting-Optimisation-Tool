import { Helmet } from "react-helmet-async";
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useAsyncError } from '../hooks/useAsyncError';
import { styles } from '../utils/recommend_styles';

// types for the data we get back from the api
interface Recommendation {
  species_id: number;
  rank_overall: number;
  species_common_name: string;
  species_name: string;
  score_mcda: number;
  key_reasons: string[];
}

interface ExcludedSpecies {
  id: number;
  species_common_name: string;
  species_name: string;
  reasons: string[];
}

export const RecommendationPage: React.FC = () => {
  const { token } = useAuth();
  const throwAsyncError = useAsyncError();

  // state variables to hold my data
  const [farmId, setFarmId] = useState<string>(''); // user input
  const [recs, setRecs] = useState<Recommendation[]>([]); // valid species
  const [excludes, setExcludes] = useState<ExcludedSpecies[]>([]); // excluded species

  // ui states
  const [loading, setLoading] = useState<boolean>(false); // for the loading button
  const [expandedRows, setExpandedRows] = useState<string[]>([]); // keeps track of which table rows are clicked open
  const [hasSearched, setHasSearched] = useState<boolean>(false); // so we don't show empty cards on first load

  // fetch data from the backend when the user clicks generate
  const handleGetRecs = async () => {
    if (!farmId) return; // do nothing if input is empty

    // reset everything before fetching
    setLoading(true);
    setRecs([]);
    setExcludes([]);
    setExpandedRows([]);
    setHasSearched(false);

    try {
      // api call to python backend
      const response = await fetch(`http://127.0.0.1:8080/recommendations/${farmId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(errorData);
      }

      const data = await response.json();

      // save the data to state (use empty array if null to prevent crashes)
      setRecs(data.recommendations || []);
      setExcludes(data.excluded_species || []);
      setHasSearched(true); // safe to show the cards now
    } catch (err: any) {
      throwAsyncError(err);
    } finally {
      setLoading(false); // turn off loading spinner
    }
  };

  // get progress bar color based on the score
  const getBarColor = (score: number) => {
    if (score >= 0.8) return '#28a745'; // green
    if (score >= 0.4) return '#fd7e14'; // orange
    return '#dc3545'; // red
  };

  // styles for the empty cards if there are no species in that category
  const getEmptyStateStyle = (type: 'top' | 'caut' | 'exc'): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
      padding: '20px',
      margin: '20px 0 10px 0',
      borderRadius: '6px',
      borderWidth: '1px',
      borderStyle: 'solid',
      fontSize: '0.95rem',
    };

    // return matching colors for each type
    switch (type) {
      case 'top': return { ...baseStyle, color: '#155724', backgroundColor: '#d4edda', borderColor: '#c3e6cb' };
      case 'caut': return { ...baseStyle, color: '#856404', backgroundColor: '#fff3cd', borderColor: '#ffeeba' };
      case 'exc': return { ...baseStyle, color: '#155724', backgroundColor: '#d4edda', borderColor: '#c3e6cb' }; // green because 0 excluded is a good thing
      default: return baseStyle;
    }
  };

  // returns a small icon for the empty state message
  const getEmptyStateIcon = (type: 'top' | 'caut' | 'exc') => {
    switch (type) {
      case 'top': return 'ⓘ';
      case 'caut': return '⚠';
      case 'exc': return '✓';
      default: return 'ⓘ';
    }
  };

  // formats the text inside the expanded details row
  const renderReason = (reason: string) => {
    const text = reason.toLowerCase();
    const parts = reason.split(':'); // split the factor and the result
    const factor = parts[0] ? parts[0].trim() : "";
    const result = parts[1] ? parts[1].trim() : "";

    // figure out if it's good or bad to color the text
    const isPositive = text.includes('inside') || text.includes('exact match') || text.includes('plateau');
    const isNegative = text.includes('below minimum') || text.includes('above maximum') || text.includes('no_match') || text.includes('not supported');

    const color = isPositive ? '#28a745' : (isNegative ? '#dc3545' : '#fd7e14');
    const icon = isPositive ? '✓' : (isNegative ? '✗' : '⚠');

    // capitalize factor name
    const formatFactor = (str: string) => {
      if (!str) return "";
      if (str.toLowerCase() === 'ph') return 'pH';
      return str.charAt(0).toUpperCase() + str.slice(1);
    };

    return (
      <div style={styles.reasonRow}>
        <span style={{ color, textAlign: 'left', fontWeight: (isPositive || isNegative) ? '600' : '400' }}>
          <span>{formatFactor(factor)}</span>
          {result && <span style={{ color: '#888', fontWeight: '400' }}> &nbsp;&nbsp;—&nbsp;&nbsp; {result}</span>}
        </span>
        <span style={{ color, fontSize: '1.2rem', marginLeft: '20px' }}>{icon}</span>
      </div>
    );
  };

  // open or close a single row when the Details button is clicked
  const toggleSingleRow = (rowId: string) => {
    setExpandedRows(prev =>
      prev.includes(rowId)
        ? prev.filter(id => id !== rowId) // remove it if it's already open
        : [...prev, rowId] // add it if it's closed
    );
  };

  // handle the Expand All / Collapse All button for a specific card
  const toggleAllInGroup = (rowIds: string[]) => {
    const areAllExpanded = rowIds.every(id => expandedRows.includes(id));

    if (areAllExpanded) {
      // collapse all rows for this card
      setExpandedRows(prev => prev.filter(id => !rowIds.includes(id)));
    } else {
      // expand all rows (use Set to prevent duplicates)
      setExpandedRows(prev => {
        const combined = new Set([...prev, ...rowIds]);
        return Array.from(combined);
      });
    }
  };

  // split the recommendations into two lists based on score
  const topFits = recs.filter(r => r.score_mcda >= 0.8);
  const cautionaryFits = recs.filter(r => r.score_mcda < 0.8);

  // reusable function so i don't have to copy/paste the table code twice
  const renderRecsTable = (title: string, data: Recommendation[], prefix: 'top' | 'caut', emptyMessage: string) => {
    // create unique ids like "top-1" so rows don't get mixed up
    const rowIds = data.map(item => `${prefix}-${item.species_id}`);
    const areAllExpanded = data.length > 0 && rowIds.every(id => expandedRows.includes(id));

    return (
      <div style={{ ...styles.resultsCard, flex: '1 1 300px', margin: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{title}</h3>

          {/* only show expand all button if there are items */}
          {data.length > 0 && (
            <button
              style={{ ...styles.detailsBtn, width: 'auto', padding: '4px 12px' }}
              onClick={() => toggleAllInGroup(rowIds)}
            >
              {areAllExpanded ? 'Collapse All' : 'Expand All'}
            </button>
          )}
        </div>

        {/* show empty state if no data, otherwise show the table */}
        {data.length === 0 ? (
          <div style={getEmptyStateStyle(prefix)}>
            <span style={{ fontSize: '1.2rem' }}>{getEmptyStateIcon(prefix)}</span>
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
              {/* loop through data and make a row for each species */}
              {data.map((item) => {
                const rowId = `${prefix}-${item.species_id}`;
                const isExpanded = expandedRows.includes(rowId);

                return (
                  <React.Fragment key={rowId}>
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
                        <button
                          style={styles.detailsBtn}
                          onClick={() => toggleSingleRow(rowId)}
                        >
                          {isExpanded ? 'Hide' : 'Details'}
                        </button>
                      </td>
                    </tr>

                    {/* extra row for details, only visible if clicked */}
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
              })}
            </tbody>
          </table>
        )}
      </div>
    );
  };

  // calculate ids for the excluded table to use with expand all button
  const excludedRowIds = excludes.map(item => `exc-${item.id}`);
  const areAllExcludedExpanded = excludes.length > 0 && excludedRowIds.every(id => expandedRows.includes(id));

  return (
    <div style={styles.viewContainer}>
      <Helmet>
        <title>Agroforestry Recommendation | Planting Optimisation Tool</title>
      </Helmet>
      <h2 style={styles.viewTitle}>Agroforestry Recommendations</h2>
      {/* search form */}
      <div style={styles.controls}>
        <div style={styles.inputGroup}>
          <label style={styles.label}>Farm ID</label>
          <input
            type="number"
            style={styles.input}
            value={farmId}
            onChange={(e) => setFarmId(e.target.value)}
            placeholder="e.g. 1"
          />
        </div>
        <button
          style={farmId ? styles.primaryBtn : styles.disabledBtn}
          onClick={handleGetRecs}
          disabled={loading || !farmId}
        >
          {loading ? 'Analyzing Suitability...' : 'Generate Recommendations'}
        </button>
      </div>

      {/* only show the results if the user actually searched */}
      {hasSearched && (
        // flexbox wrapper to put the cards side by side
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '20px',
          alignItems: 'flex-start',
          width: '100%'
        }}>

          {/* render the first two cards using the helper function */}
          {renderRecsTable(
            'Top Fit Species',
            topFits,
            'top',
            'No highly suitable species found for this farm.'
          )}

          {renderRecsTable(
            'Cautionary Species',
            cautionaryFits,
            'caut',
            'No species with moderate suitability found.'
          )}

          {/* excluded card is manual because the data is slightly different (no score, different keys) */}
          <div style={{ ...styles.resultsCard, flex: '1 1 300px', margin: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Excluded Species</h3>
              {excludes.length > 0 && (
                <button
                  style={{ ...styles.detailsBtn, width: 'auto', padding: '4px 12px' }}
                  onClick={() => toggleAllInGroup(excludedRowIds)}
                >
                  {areAllExcludedExpanded ? 'Collapse All' : 'Expand All'}
                </button>
              )}
            </div>

            {/* empty state */}
            {excludes.length === 0 ? (
              <div style={getEmptyStateStyle('exc')}>
                <span style={{ fontSize: '1.2rem' }}>{getEmptyStateIcon('exc')}</span>
                <span>No species were excluded for this farm.</span>
              </div>
            ) : (
              // actual table
              <table style={styles.table}>
                <thead>
                  <tr style={styles.tableHeader}>
                    <th style={styles.th}>Species</th>
                    <th style={styles.th}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {excludes.map((item) => {
                    const rowId = `exc-${item.id}`;
                    const isExpanded = expandedRows.includes(rowId);

                    return (
                      <React.Fragment key={rowId}>
                        <tr style={styles.tr}>
                          <td style={styles.td}>
                            <div style={styles.primaryName}>{item.species_common_name}</div>
                            <div style={styles.secondaryName}>{item.species_name}</div>
                          </td>
                          <td style={styles.td}>
                            <button
                              style={styles.detailsBtn}
                              onClick={() => toggleSingleRow(rowId)}
                            >
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
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationPage;
