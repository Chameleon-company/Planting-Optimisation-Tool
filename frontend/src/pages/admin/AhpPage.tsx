import { useState, useEffect } from 'react';

import { Helmet } from 'react-helmet-async';
import { useAhpFactors, useAhpCalculation } from '@/hooks/useAhp';
import { styles } from '@/utils/ahp_styles';

import AhpHeader from '@/components/ahp/AhpHeader';
import { SpeciesSelector } from '@/components/ahp/SpeciesSelector';
import AhpComparison from '@/components/ahp/AhpComparison';
import AhpResultsTable from '@/components/ahp/AhpResultsTable';

export default function AhpPage() {
    // Custom Hooks
    const { factorsList, isLoading: isConfigLoading } = useAhpFactors();
    const { results, isCalculating, handleCalculate, resetCalculation } = useAhpCalculation();

    // Local Page State
    const [selectedSpeciesName, setSelectedSpeciesName] = useState<string>('');
    const [selectedSpeciesId, setSelectedSpeciesId] = useState<number | null>(null);
    const [isComparing, setIsComparing] = useState<boolean>(false);

    useEffect(() => {
        const handleBeforeUnload = (e: BeforeUnloadEvent) => {
            if (isComparing) {
                e.preventDefault();
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);
        return () => window.removeEventListener('beforeunload', handleBeforeUnload);
    }, [isComparing]);

    const startComparison = () => {
        if (selectedSpeciesName) setIsComparing(true);
    };

    const submitMatrix = (matrix: number[][]) => {
        if (selectedSpeciesId !== null) {
            handleCalculate({
                species_id: selectedSpeciesId,
                matrix: matrix
            });
        }
        setIsComparing(false); // Close comparison UI, wait for results
    };

    // Completely resets the UI (for when it is consistent)
    const handleReset = () => {
        setSelectedSpeciesName('');
        setSelectedSpeciesId(null);
        setIsComparing(false);
        resetCalculation();
    };

    // Only resets the calculation, keeping the species selected (for when it is inconsistent)
    const handleRetry = () => {
        resetCalculation(); // Clear the bad results
        setIsComparing(true); // Jump straight back into the comparison matrix
    };

    // Function to drop out of an active profiling session
    const handleCancelProfiling = () => {
        setIsComparing(false);
        setSelectedSpeciesId(null);
        setSelectedSpeciesName('');
    };

    return (
        <div style={styles.viewContainer}>
            <Helmet>
                <title>AHP Expert Weighting | Planting Optimisation Tool</title>
            </Helmet>

            <AhpHeader />

            {/* The Control Panel */}
            <div style={styles.controls}>
                <div style={styles.inputGroup}>
                    <SpeciesSelector
                        isDisabled={isComparing || isCalculating || !!results}
                        onSpeciesSelect={(id, name) => {
                            setSelectedSpeciesId(id);
                            setSelectedSpeciesName(name);
                        }}
                    />
                </div>
                <button
                    style={selectedSpeciesId !== null && !isComparing && !results ? styles.primaryBtn : { ...styles.primaryBtn, ...styles.disabledBtn }}
                    onClick={startComparison}
                    disabled={!selectedSpeciesName || isComparing || !!results || isConfigLoading}
                >
                    {isConfigLoading ? 'Loading Factors...' : 'Start Profiling'}
                </button>
            </div>

            {/* State 1: Active Comparison Matrix */}
            {isComparing && factorsList && !results && (
                <AhpComparison
                    factors={factorsList.factors}
                    speciesName={selectedSpeciesName}
                    onComplete={submitMatrix}
                    onCancel={handleCancelProfiling}
                />
            )}

            {/* State 2: Loading Weights */}
            {isCalculating && (
                <div style={styles.resultsCard}>
                    <p>Calculating Eigenvector Weights...</p>
                </div>
            )}

            {/* State 3: Results Display */}
            {results && (
                <AhpResultsTable
                    data={results}
                    speciesName={selectedSpeciesName}
                    onReset={handleReset}
                    onRetry={handleRetry}
                />
            )}
        </div>
    );
}