import type { CalculatorResult as CalculatorResultType } from "@/hooks/useCalculator";
import "./calculator.css";

interface Props {
  result: CalculatorResultType;
}

export default function CalculatorResult({ result }: Props) {
  return (
    <div className="calc-results-card">
      <h3>Estimation Results</h3>

      <div className="calc-result-item">
        <span className="calc-result-label">Pre-slope Sapling Count</span>
        <span className="calc-result-value">{result.pre_slope_count}</span>
      </div>

      <div className="calc-result-item">
        <span className="calc-result-label">Final Sapling Count</span>
        <span className="calc-result-value">{result.aligned_count}</span>
      </div>

      <div className="calc-result-item">
        <span className="calc-result-label">Optimal Angle</span>
        <span className="calc-result-value">
          {`${result.optimal_angle.toFixed(2)}°`}
        </span>
      </div>
    </div>
  );
}
