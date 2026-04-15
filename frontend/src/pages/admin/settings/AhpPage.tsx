import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import {
  useAhpSpecies,
  useAhpFactors,
  useAhpCalculation,
} from "@/hooks/useAhp";

import AhpHeader from "@/components/ahp/AhpHeader";
import { SpeciesSelector } from "@/components/ahp/SpeciesSelector";
import AhpComparison from "@/components/ahp/AhpComparison";
import AhpResultsTable from "@/components/ahp/AhpResultsTable";

export default function AhpPage() {
  // Custom Hooks
  const { error: speciesError } = useAhpSpecies();
  const {
    factorsList,
    isLoading: isConfigLoading,
    error: factorsError,
  } = useAhpFactors();
  const {
    results,
    isCalculating,
    handleCalculate,
    resetCalculation,
    error: calcError,
  } = useAhpCalculation();

  // Local Page State
  const [selectedSpeciesName, setSelectedSpeciesName] = useState<string>("");
  const [selectedSpeciesId, setSelectedSpeciesId] = useState<number | null>(
    null
  );
  const [isComparing, setIsComparing] = useState<boolean>(false);

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isComparing) {
        e.preventDefault();
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [isComparing]);

  const startComparison = () => {
    if (selectedSpeciesName) setIsComparing(true);
  };

  const submitMatrix = (matrix: number[][]) => {
    if (selectedSpeciesId !== null) {
      handleCalculate({
        species_id: selectedSpeciesId,
        matrix: matrix,
      });
    }
    setIsComparing(false); // Close comparison UI, wait for results
  };

  // Completely resets the UI (for when it is consistent)
  const handleReset = () => {
    setSelectedSpeciesName("");
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
  const [resetKey, setResetKey] = useState(0);
  const handleCancelProfiling = () => {
    setIsComparing(false);
    setSelectedSpeciesId(null);
    setSelectedSpeciesName("");
    setResetKey(prev => prev + 1); // Increment to force a fresh dropdown
  };

  // Combine errors for display
  const globalError = speciesError || factorsError;

  return (
    <div className="ahp-view-container">
      <Helmet>
        <title>AHP Expert Weighting | Planting Optimisation Tool</title>
      </Helmet>

      {/* Back Button */}
      <div style={{ marginBottom: "24px" }}>
        <Link
          to="/admin/settings/weighting"
          style={{
            textDecoration: "none",
            color: "#4f46e5",
            fontWeight: "500",
          }}
        >
          ← Back to Weighting Methods
        </Link>
      </div>

      <AhpHeader />

      {/* Display local errors */}
      {globalError && (
        <div className="ahp-error-message">
          <p>
            <strong>Error:</strong> {globalError}
          </p>
          {calcError && <button onClick={handleRetry}>Try Again</button>}
        </div>
      )}

      {/* The Control Panel */}
      <div className="ahp-controls">
        <div className="ahp-input-group">
          <SpeciesSelector
            key={resetKey}
            isDisabled={
              isComparing || isCalculating || !!results || !!globalError
            }
            onSpeciesSelect={(id, name) => {
              setSelectedSpeciesId(id);
              setSelectedSpeciesName(name);
            }}
          />
        </div>
        <button
          className={
            selectedSpeciesId !== null && !isComparing && !results
              ? "ahp-primary-btn"
              : "ahp-primary-btn ahp-disabled-btn"
          }
          onClick={startComparison}
          disabled={
            !selectedSpeciesName || isComparing || !!results || isConfigLoading
          }
        >
          {isConfigLoading ? "Loading Factors..." : "Start Profiling"}
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
        <div className="ahp-results-card">
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
