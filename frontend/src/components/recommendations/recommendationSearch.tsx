import { useState } from "react";
import { styles } from "../../utils/recommend_styles";

interface RecommendationSearchProps {
    onSearch: (farmId: string) => void;
    isLoading: boolean;
}

export default function RecommendationSearch({ onSearch, isLoading }: RecommendationSearchProps) {
    const [searchInput, setSearchInput] = useState("");

    const handleSearch = () => {
        if (!searchInput.trim()) return;
        onSearch(searchInput);
    };

    return (
        <div style={styles.controls}>
            <div style={styles.inputGroup}>
                <label style={styles.label}>Farm ID</label>
                <input
                    type="number"
                    style={styles.input}
                    value={searchInput}
                    placeholder="e.g. 1"
                    onChange={e => setSearchInput(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && handleSearch()}
                />
            </div>
            <button
                style={searchInput ? styles.primaryBtn : styles.disabledBtn}
                onClick={handleSearch}
                disabled={isLoading || !searchInput}
            >
                {isLoading ? 'Analyzing Suitability...' : 'Generate Recommendations'}
            </button>
        </div>
    );
}