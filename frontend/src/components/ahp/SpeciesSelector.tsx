// src/components/ahp/SpeciesSelector.tsx
import React from 'react';
import { useAhpSpecies } from '@/hooks/useAhp';
import { styles } from '@/utils/ahp_styles';

interface SpeciesSelectorProps {
    onSpeciesSelect: (speciesId: number, speciesName: string) => void;
    isDisabled?: boolean;
}

export function SpeciesSelector({ onSpeciesSelect, isDisabled }: SpeciesSelectorProps) {
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
        <div style={styles.inputGroup}>
            <label htmlFor="species-select" style={styles.label}>
                Select a Species
            </label>

            <select
                id="species-select"
                onChange={handleChange}
                style={styles.select}
                defaultValue=""
                disabled={isLoading || isDisabled}
            >
                <option value="" disabled>
                    {isLoading ? 'Loading species...' : '-- Choose a species --'}
                </option>

                {speciesList.map((species) => (
                    <option key={species.id} value={species.id}>
                        {species.common_name} ({species.name})
                    </option>
                ))}
            </select>
        </div>
    );
}