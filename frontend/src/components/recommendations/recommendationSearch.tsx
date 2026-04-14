import { useState } from "react";
import "@/pages/recommendations.css";

interface RecommendationSearchProps {
  onSearch: (farmId: string) => void;
  isLoading: boolean;
}

export default function RecommendationSearch({
  onSearch,
  isLoading,
}: RecommendationSearchProps) {
  const [searchInput, setSearchInput] = useState("");

  const handleSearch = () => {
    if (!searchInput.trim()) return;
    onSearch(searchInput);
  };

  return (
    <div className="rec-controls">
      <div className="rec-input-group">
        <label className="rec-label">Farm ID</label>
        <input
          type="number"
          className="rec-input"
          value={searchInput}
          placeholder="e.g. 1"
          onChange={e => setSearchInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSearch()}
        />
      </div>
      <button
        className="rec-primary-btn"
        onClick={handleSearch}
        disabled={isLoading || !searchInput.trim()}
      >
        {isLoading ? "Analyzing Suitability..." : "Generate Recommendations"}
      </button>
    </div>
  );
}
