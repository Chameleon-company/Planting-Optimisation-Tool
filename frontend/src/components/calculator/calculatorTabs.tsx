import { useRef } from "react";
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
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  if (results.length <= 1) return null;

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    let nextIndex: number | null = null;

    if (e.key === "ArrowRight") {
      nextIndex = (index + 1) % results.length;
    } else if (e.key === "ArrowLeft") {
      nextIndex = (index - 1 + results.length) % results.length;
    } else if (e.key === "Home") {
      nextIndex = 0;
    } else if (e.key === "End") {
      nextIndex = results.length - 1;
    }

    if (nextIndex !== null) {
      e.preventDefault();
      onSelect(results[nextIndex].farm_id);
      tabRefs.current[nextIndex]?.focus();
    }
  };

  return (
    <div className="calc-tabs" role="tablist" aria-label="Searched farms">
      {results.map((result, index) => {
        const isActive = result.farm_id === selectedFarmId;
        const failed = result.status === "failed";
        return (
          <button
            key={result.farm_id}
            ref={element => {
              tabRefs.current[index] = element;
            }}
            role="tab"
            aria-selected={isActive}
            tabIndex={isActive ? 0 : -1}
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
            onKeyDown={e => handleKeyDown(e, index)}
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
