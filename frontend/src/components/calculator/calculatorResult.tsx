import type { FarmEstimationResult } from "@/hooks/useCalculator";
import "./calculator.css";

interface Props {
  result: FarmEstimationResult;
}

function formatAngle(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return `${value.toFixed(2)}°`;
}

function formatCount(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return String(value);
}

export default function CalculatorResult({ result }: Props) {
  return (
    <div className="calc-results-card">
      <h3>Estimation Results - Farm {result.farm_id}</h3>

      <div className="calc-result-item">
        <span className="calc-result-label">Pre-slope Sapling Count</span>
        <span className="calc-result-value">
          {formatCount(result.pre_slope_count)}
        </span>
      </div>

      <div className="calc-result-item">
        <span className="calc-result-label">Final Sapling Count</span>
        <span className="calc-result-value">
          {formatCount(result.aligned_count)}
        </span>
      </div>

      <div className="calc-result-item">
        <span className="calc-result-label">Optimal Angle</span>
        <span className="calc-result-value">
          {formatAngle(result.optimal_angle)}
        </span>
      </div>
    </div>
  );
}
