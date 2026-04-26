import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { useCalculator } from "@/hooks/useCalculator";
import CalculatorHeader from "@/components/calculator/calculatorHeader";
import CalculatorSearch from "@/components/calculator/calculatorSearch";
import CalculatorResult from "@/components/calculator/calculatorResult";
import "@/components/calculator/calculator.css";

export default function CalculatorPage() {
  const [farmId, setFarmId] = useState("");
  const { result, isLoading, hasSearched, error } = useCalculator(farmId);

  return (
    <div className="calc-view-container">
      <Helmet>
        <title>Sapling Calculator | Planting Optimisation Tool</title>
      </Helmet>

      <CalculatorHeader />

      <div className="calc-controls-wrapper">
        <CalculatorSearch onSearch={setFarmId} isLoading={isLoading} />
      </div>

      {error && (
        <div className="calc-error-message">
          <p>
            <strong>Error:</strong> {error}
          </p>
        </div>
      )}

      {hasSearched && result && (
        <div style={{ marginTop: "20px" }}>
          <CalculatorResult result={result} />
        </div>
      )}
    </div>
  );
}
