import { useState } from "react";
import type { CalcParams } from "@/hooks/useCalculator";
import { DEFAULT_CALC_PARAMS } from "@/hooks/useCalculator";
import "./calculator.css";

interface CalculatorSearchProps {
  onSearch: (farmIds: number[], params: CalcParams) => void;
  isLoading: boolean;
}

// split separated string into unique integer IDs
function parseFarmIds(raw: string): number[] {
  const ids = raw
    .split(/[\s,]+/)
    .map(s => s.trim())
    .filter(s => s !== "")
    .map(Number)
    .filter(n => Number.isInteger(n) && n > 0);
  return Array.from(new Set(ids));
}

export default function CalculatorSearch({
  onSearch,
  isLoading,
}: CalculatorSearchProps) {
  const [farmIdsInput, setFarmIdsInput] = useState("");
  const [spacingX, setSpacingX] = useState(DEFAULT_CALC_PARAMS.spacingX);
  const [spacingY, setSpacingY] = useState(DEFAULT_CALC_PARAMS.spacingY);
  const [maxSlope, setMaxSlope] = useState(DEFAULT_CALC_PARAMS.maxSlope);

  const parsedIds = parseFarmIds(farmIdsInput);
  const canSearch =
    parsedIds.length > 0 &&
    spacingX > 0 &&
    spacingY > 0 &&
    maxSlope > 0 &&
    maxSlope < 90;

  const handleSearch = () => {
    if (!canSearch) return;
    onSearch(parsedIds, { spacingX, spacingY, maxSlope });
  };

  return (
    <div className="calc-controls">
      <div className="calc-input-group">
        <label className="calc-label" htmlFor="calc-farm-ids">
          Farm ID(s)
        </label>
        <input
          id="calc-farm-ids"
          type="text"
          className="calc-input"
          value={farmIdsInput}
          placeholder="e.g. 1, 2, 3"
          onChange={e => setFarmIdsInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSearch()}
        />
      </div>

      <div className="calc-input-group">
        <label className="calc-label" htmlFor="calc-spacing-x">
          Spacing X (m)
        </label>
        <input
          id="calc-spacing-x"
          type="number"
          className="calc-input"
          value={spacingX}
          min={0.1}
          step={0.1}
          onChange={e => setSpacingX(Number(e.target.value))}
        />
      </div>

      <div className="calc-input-group">
        <label className="calc-label" htmlFor="calc-spacing-y">
          Spacing Y (m)
        </label>
        <input
          id="calc-spacing-y"
          type="number"
          className="calc-input"
          value={spacingY}
          min={0.1}
          step={0.1}
          onChange={e => setSpacingY(Number(e.target.value))}
        />
      </div>

      <div className="calc-input-group">
        <label className="calc-label" htmlFor="calc-max-slope">
          Max Slope (°)
        </label>
        <input
          id="calc-max-slope"
          type="number"
          className="calc-input"
          value={maxSlope}
          min={0}
          max={90}
          step={1}
          onChange={e => setMaxSlope(Number(e.target.value))}
        />
      </div>

      <button
        className="btn-primary"
        onClick={handleSearch}
        disabled={isLoading || !canSearch}
      >
        {isLoading ? "Estimating Saplings..." : "Generate Planting Plan"}
      </button>
    </div>
  );
}
