import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { Helmet } from "react-helmet-async";

import { useCalculator, DEFAULT_CALC_PARAMS } from "@/hooks/useCalculator";
import type { CalcParams } from "@/hooks/useCalculator";
import { AGGREGATE_ID } from "@/hooks/useCalculator";
import { useFarmMap } from "@/hooks/useFarmMap";

import CalculatorHeader from "@/components/calculator/calculatorHeader";
import CalculatorSearch from "@/components/calculator/calculatorSearch";
import {
  CalculatorResult,
  CalculatorAggregate,
} from "@/components/calculator/calculatorResult";
import CalculatorTabs from "@/components/calculator/calculatorTabs";
import FarmMap from "@/components/calculator/calculatorFarmMap";
import CombinedFarmMap from "@/components/calculator/calculatorCombinedMap";

import "@/components/calculator/calculator.css";

export default function CalculatorPage() {
  const [farmIds, setFarmIds] = useState<number[]>([]);
  const [calcParams, setCalcParams] = useState<CalcParams>(DEFAULT_CALC_PARAMS);
  const [selectedFarmId, setSelectedFarmId] = useState<number | null>(null);
  const [shouldRun, setShouldRun] = useState(false);

  const { results, isLoading, hasSearched, error } = useCalculator(
    farmIds,
    calcParams,
    shouldRun
  );

  useEffect(() => {
    if (error) {
      toast.error(error);
    }
  }, [error]);

  const showAggregate = selectedFarmId === AGGREGATE_ID;

  const selectedResult = showAggregate
    ? null
    : (results.find(r => r.farm_id === selectedFarmId) ?? null);

  const mapFarmId =
    selectedResult?.status === "success" ? selectedFarmId : null;
  const { boundary, grid } = useFarmMap(mapFarmId);

  useEffect(() => {
    if (results.length === 0) {
      setSelectedFarmId(null);
      return;
    }
    const successful = results.filter(r => r.status === "success");
    const firstSuccess = successful[0];
    setSelectedFarmId(
      successful.length > 1
        ? AGGREGATE_ID
        : (firstSuccess ?? results[0]).farm_id
    );
  }, [results]);

  const handleSearch = (newFarmIds: number[], newParams: CalcParams) => {
    setFarmIds(newFarmIds);
    setCalcParams(newParams);
    setShouldRun(true);
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

          {showAggregate ? (
            <div className="calc-farm-panel">
              <CalculatorAggregate results={results} />
              <CombinedFarmMap
                results={results}
                spacingY={calcParams.spacingY}
              />
            </div>
          ) : selectedResult && selectedResult.status === "success" ? (
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
