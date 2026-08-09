import type { FarmEstimationResult } from "@/hooks/useCalculator";
import "./calculator.css";

interface Props {
  results: FarmEstimationResult[];
  selectedFarmId: number | null;
  onSelect: (farmId: number) => void;
}

export default function CalculatorTabs({
  results,
  selectedFarmId,
  onSelect,
}: Props) {
  if (results.length <= 1) return null;

  return (
    <div className="calc-tabs" role="tablist" aria-label="Searched farms">
      {results.map(result => {
        const isActive = result.farm_id === selectedFarmId;
        const failed = result.status === "failed";
        return (
          <button
            key={result.farm_id}
            role="tab"
            aria-selected={isActive}
            title={
              failed
                ? (result.message ?? "Estimation failed")
                : `Farm ${result.farm_id}`
            }
            className={[
              "calc-tab",
              isActive ? "calc-tab-active" : "",
              failed ? "calc-tab-failed" : "",
            ]
              .filter(Boolean)
              .join(" ")}
            onClick={() => onSelect(result.farm_id)}
          >
            <span className="calc-tab-status" aria-hidden="true">
              {failed ? "⚠" : "●"}
            </span>
            Farm {result.farm_id}
          </button>
        );
      })}
    </div>
  );
}
