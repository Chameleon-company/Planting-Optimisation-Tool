import { useRef } from "react";
import type { FarmEstimationResult } from "@/hooks/useCalculator";
import { AGGREGATE_ID } from "@/hooks/useCalculator";
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
  // Create array of button elements
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  // If only one farm suceeded, do not create aggregate page
  const successCount = results.filter(r => r.status === "success").length;
  const showAggregate = successCount > 1;

  if (results.length <= 1 && !showAggregate) return null;

  // If showAggregate is true, then add pre-determined AGGREGATE_ID to start of results array, otherwise just map array
  const tabIds = showAggregate
    ? [AGGREGATE_ID, ...results.map(r => r.farm_id)]
    : results.map(r => r.farm_id);

  // Receive keyboard event
  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    let nextIndex: number | null = null;

    // If key is right, increase index by 1, if left decrease, home to start, end to end of array
    if (e.key === "ArrowRight") {
      nextIndex = (index + 1) % tabIds.length;
    } else if (e.key === "ArrowLeft") {
      nextIndex = (index - 1 + tabIds.length) % tabIds.length;
    } else if (e.key === "Home") {
      nextIndex = 0;
    } else if (e.key === "End") {
      nextIndex = tabIds.length - 1;
    }

    // If key is pressed, prevent default behaivour, select next tabID, set keyboard focus to new tabId
    if (nextIndex !== null) {
      e.preventDefault();
      onSelect(tabIds[nextIndex]);
      tabRefs.current[nextIndex]?.focus();
    }
  };

  return (
    <div className="calc-tabs" role="tablist" aria-label="Searched farms">
      {/* Loops over each farm for tab */}
      {tabIds.map((id, index) => {
        // finds if active, if tab is aggregate tab, results from farm id, and if failed
        const isActive = id === selectedFarmId;
        const isAggregate = id === AGGREGATE_ID;
        const result = isAggregate ? null : results.find(r => r.farm_id === id);
        const failed = result?.status === "failed";

        // For each farm create button for that farm using variables from the result
        return (
          <button
            key={id}
            // Set reference for button to be current element stashed in tabRefs
            ref={element => {
              tabRefs.current[index] = element;
            }}
            role="tab"
            aria-selected={isActive}
            // Set active tab to an index of 0, so when tab is pressed it highlights active tab
            tabIndex={isActive ? 0 : -1}
            // Set title if aggregate to all farms, if failed display message, if neither is farm ${id}
            title={
              isAggregate
                ? "Combined view of all farms"
                : failed
                  ? (result?.message ?? "Estimation failed")
                  : `Farm ${id}`
            }
            // Set class name to calc-tab, depending on variables set css to more specific format
            className={[
              "calc-tab",
              isActive ? "calc-tab-active" : "",
              isAggregate ? "calc-tab-aggregate" : "",
              failed ? "calc-tab-failed" : "",
            ]
              // Filter by if true, if true, join class name into one string
              .filter(Boolean)
              .join(" ")}
            // If clicked, set id to selected tab, if key pressed call handleKeyDown
            onClick={() => onSelect(id)}
            onKeyDown={e => handleKeyDown(e, index)}
          >
            {/* Create text for name of tab */}
            <span className="calc-tab-status" aria-hidden="true">
              {isAggregate ? "Σ" : failed ? "⚠" : "●"}
            </span>
            {isAggregate ? "Aggregate" : `Farm ${id}`}
          </button>
        );
      })}
    </div>
  );
}
