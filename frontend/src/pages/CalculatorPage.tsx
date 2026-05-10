import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { useCalculator, DEFAULT_CALC_PARAMS } from "@/hooks/useCalculator";
import type { CalcParams } from "@/hooks/useCalculator";
import { useFarmMap } from "@/hooks/useFarmMap";
import CalculatorHeader from "@/components/calculator/calculatorHeader";
import CalculatorSearch from "@/components/calculator/calculatorSearch";
import CalculatorResult from "@/components/calculator/calculatorResult";
import FarmMap from "@/components/calculator/FarmMap";
import "@/components/calculator/calculator.css";

export default function CalculatorPage() {
  const [farmId, setFarmId] = useState("");
  const [calcParams, setCalcParams] = useState<CalcParams>(DEFAULT_CALC_PARAMS);
  const { result, isLoading, hasSearched, error } = useCalculator(
    farmId,
    calcParams
  );
  const { boundary, grid } = useFarmMap(result ? Number(farmId) : null);

  const handleSearch = (newFarmId: string, newParams: CalcParams) => {
    setFarmId(newFarmId);
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

      {hasSearched && result && (
        <div className="calc-results-layout">
          <CalculatorResult result={result} />
          <FarmMap
            boundary={boundary}
            grid={grid}
            optimalAngle={result.optimal_angle}
            spacingY={calcParams.spacingY}
          />
        </div>
      )}
    </div>
  );
}
