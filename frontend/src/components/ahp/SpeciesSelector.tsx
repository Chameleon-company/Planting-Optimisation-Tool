import React from "react";
import { useAhpSpecies } from "@/hooks/useAhp";

interface SpeciesSelectorProps {
  onSpeciesSelect: (speciesId: number, speciesName: string) => void;
  isDisabled?: boolean;
}

export function SpeciesSelector({
  onSpeciesSelect,
  isDisabled,
}: SpeciesSelectorProps) {
  const { speciesList, isLoading } = useAhpSpecies();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = Number(e.target.value);

    // Find the full species object so we can pass both ID and Name back up
    const selectedSpecies = speciesList.find(s => s.id === selectedId);

    if (selectedSpecies) {
      onSpeciesSelect(selectedSpecies.id, selectedSpecies.common_name);
    }
  };

  return (
    <div className="ahp-input-group">
      <label htmlFor="species-select" className="ahp-label">
        Select a Species
      </label>

      <select
        id="species-select"
        onChange={handleChange}
        className="ahp-select"
        defaultValue=""
        disabled={isLoading || isDisabled}
      >
        <option value="" disabled>
          {isLoading ? "Loading species..." : "-- Choose a species --"}
        </option>

        {speciesList.map(species => (
          <option key={species.id} value={species.id}>
            {species.common_name} ({species.name})
          </option>
        ))}
      </select>
    </div>
  );
}
