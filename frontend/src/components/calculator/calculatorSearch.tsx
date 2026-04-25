import { useState } from "react";
import "./calculator.css";

interface CalculatorSearchProps {
  onSearch: (farmId: string) => void;
  isLoading: boolean;
}

export default function CalculatorSearch({
  onSearch,
  isLoading,
}: CalculatorSearchProps) {
  const [input, setInput] = useState("");

  const handleSearch = () => {
    if (!input.trim()) return;
    onSearch(input);
  };

  return (
    <div className="calc-controls">
      <div className="calc-input-group">
        <label className="calc-label">Farm ID</label>
        <input
          type="number"
          className="calc-input"
          value={input}
          placeholder="e.g. 1"
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSearch()}
        />
      </div>

      <button
        className="calc-primary-btn"
        onClick={handleSearch}
        disabled={isLoading || !input.trim()}
      >
        {isLoading ? "Estimating Saplings..." : "Generate Planting Plan"}
      </button>
    </div>
  );
}
