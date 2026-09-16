import type { FarmEstimationResult } from "@/hooks/useCalculator";
import "./calculator.css";

interface Row {
  label: string;
  value: string;
}

// Format Angle function, pinning number of decimals and adding degree
function formatAngle(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return `${value.toFixed(2)}°`;
}

// Format Count function, converting value into string
function formatCount(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return String(value);
}

// Sum function, give array of farm results, only allowing fields in FarmEstimationResult, returning a number
function sum(
  results: FarmEstimationResult[],
  key: keyof FarmEstimationResult
): number {
  // Starting total at 0, add current.searchedforfield's number as number, if none add 0, looping through all farms
  return results.reduce(
    (total, current) => total + ((current[key] as number | null) ?? 0),
    0
  );
}

// ResultCard function, taking title and rows as props, set title to title, and map
// each handed row to table given row title and value, adaptable component
function ResultCard({ title, rows }: { title: string; rows: Row[] }) {
  return (
    <div className="calc-results-card">
      <h3>{title}</h3>
      {rows.map(row => (
        <div className="calc-result-item" key={row.label}>
          <span className="calc-result-label">{row.label}</span>
          <span className="calc-result-value">{row.value}</span>
        </div>
      ))}
    </div>
  );
}

// For calculator results for singular farms, take a farm restult, and hand result card the title and row values
export function CalculatorResult({ result }: { result: FarmEstimationResult }) {
  return (
    <ResultCard
      title={`Estimation Results - Farm ${result.farm_id}`}
      rows={[
        {
          label: "Pre-slope Sapling Count",
          value: formatCount(result.pre_slope_count),
        },
        {
          label: "Total Sapling Count",
          value: formatCount(result.aligned_count),
        },
        {
          label: "Saplings Available to Plant",
          value: formatCount(result.additional_sapling_count),
        },
        { label: "Optimal Angle", value: formatAngle(result.optimal_angle) },
      ]}
    />
  );
}

// For calculator results for aggregate of farms, call sum and combine results for all successful farms
export function CalculatorAggregate({
  results,
}: {
  results: FarmEstimationResult[];
}) {
  const successful = results.filter(r => r.status === "success");
  return (
    <ResultCard
      title={`Aggregate of ${successful.length} farms`}
      rows={[
        {
          label: "Pre-slope Sapling Count",
          value: formatCount(sum(successful, "pre_slope_count")),
        },
        {
          label: "Total Sapling Count",
          value: formatCount(sum(successful, "aligned_count")),
        },
        {
          label: "Saplings Available to Plant",
          value: formatCount(sum(successful, "additional_sapling_count")),
        },
      ]}
    />
  );
}
