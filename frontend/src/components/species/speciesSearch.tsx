import { useState } from "react";

// Create interface for props, query as part of onSearch function is set as string and promises void
// Loading set to a boolean
interface SpeciesSearchProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

export default function SpeciesSearch({
  onSearch,
  isLoading,
}: SpeciesSearchProps) {
  // UseState searchInput and setSearchInput
  const [searchInput, setSearchInput] = useState("");

  // If searchInput cannot be trimmed return, otherwise hand to onSearch in SpeciesPage
  const handleSearch = () => {
    if (!searchInput.trim()) return;
    onSearch(searchInput);
  };

  return (
    <section className="species-container">
      <div className="species-search">
        <label className="search-label">Search species</label>
        <div className="search-row">
          {/* Search input, its value is updating searchInput 
            When onChange is triggered, i.e when a key is pressed, 
            setSearchInput to current value in textbox 
            When Enter or search-btn is pressed call handleSearch*/}
          <input
            className="search-input"
            type="text"
            value={searchInput}
            placeholder="Enter keywords like '2000mm' or 'boundary systems"
            onChange={e => setSearchInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSearch()}
          />
          <button className="search-btn" onClick={handleSearch}>
            <span className="search-icon">🔍</span>
            <span>{isLoading ? "..." : "Search"}</span>
          </button>
        </div>
      </div>
    </section>
  );
}
