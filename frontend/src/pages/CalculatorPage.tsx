import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";

import { useCalculator, DEFAULT_CALC_PARAMS } from "@/hooks/useCalculator";
import type { CalcParams } from "@/hooks/useCalculator";
import { useFarmMap } from "@/hooks/useFarmMap";

import CalculatorHeader from "@/components/calculator/calculatorHeader";
import CalculatorSearch from "@/components/calculator/calculatorSearch";
import CalculatorResult from "@/components/calculator/calculatorResult";
import CalculatorTabs from "@/components/calculator/calculatorTabs";
import FarmMap from "@/components/calculator/FarmMap";

import "@/components/calculator/calculator.css";

export default function CalculatorPage() {
  const [farmIds, setFarmIds] = useState<number[]>([]);
  const [calcParams, setCalcParams] = useState<CalcParams>(DEFAULT_CALC_PARAMS);
  const [selectedFarmId, setSelectedFarmId] = useState<number | null>(null);

  const { results, isLoading, hasSearched, error } = useCalculator(
    farmIds,
    calcParams
  );

  const selectedResult =
    results.find(r => r.farm_id === selectedFarmId) ?? null;

  // Only load the map for a farm that actually produced a grid
  const mapFarmId =
    selectedResult?.status === "success" ? selectedFarmId : null;
  const { boundary, grid } = useFarmMap(mapFarmId);

  // When successful search focus the first successful farm
  useEffect(() => {
    if (results.length === 0) {
      setSelectedFarmId(null);
      return;
    }
    const firstSuccess = results.find(r => r.status === "success");
    setSelectedFarmId((firstSuccess ?? results[0]).farm_id);
  }, [results]);

  const handleSearch = (newFarmIds: number[], newParams: CalcParams) => {
    setFarmIds(newFarmIds);
    setCalcParams(newParams);
  };

  return (
    <div className="calc-view-container">
      <Helmet>
        <title>Sapling Calculator | Planting Optimisation Tool</title>
      </Helmet>

      <CalculatorHeader />

      <div className="calc-controls-wrapper">
        <CalculatorSearch onSearch={handleSearch} isLoading={isLoading} />
      </div>

      {error && (
        <div className="calc-error-message">
          <p>
            <strong>Error:</strong> {error}
          </p>
        </div>
      )}

      {hasSearched && results.length > 0 && (
        <div className="calc-results-section">
          <CalculatorTabs
            results={results}
            selectedFarmId={selectedFarmId}
            onSelect={setSelectedFarmId}
          />

          {selectedResult && selectedResult.status === "success" ? (
            <div className="calc-farm-panel">
              <CalculatorResult result={selectedResult} />
              <FarmMap
                boundary={boundary}
                grid={grid}
                optimalAngle={selectedResult.optimal_angle ?? null}
                spacingY={calcParams.spacingY}
              />
            </div>
          ) : selectedResult ? (
            <div className="calc-error-message">
              <p>
                <strong>Farm {selectedResult.farm_id} failed:</strong>{" "}
                {selectedResult.message ??
                  "Estimation could not be completed for this farm."}
              </p>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
