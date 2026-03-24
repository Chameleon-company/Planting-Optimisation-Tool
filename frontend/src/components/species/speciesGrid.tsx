import SpeciesCard from "./speciesCard";
import { Species } from "../../utils/contentfulClient";

// Create interface for SpeciesGrid Props, species of Species type array,
// onCardClick function taking an item of species and promising void when finished calling
interface SpeciesGridProps {
  species: Species[];
  onCardClick: (item: Species) => void;
}

export default function SpeciesGrid({
  species,
  onCardClick,
}: SpeciesGridProps) {
  // If the species array handed by SpeciesPage is empty, hand back empty <p>
  if (species.length === 0) {
    return (
      <p className="species-empty">No species found matching your criteria.</p>
    );
  }

  // Otherwise return the Species as a grid using the .map function with each item
  // Keyed to the SpeciesCard component, with a key, item, and onClick function promising onCardClick
  return (
    <div className="species-grid">
      {species.map(item => (
        <SpeciesCard
          key={item.sys.id}
          item={item}
          onClick={() => onCardClick(item)}
        />
      ))}
    </div>
  );
}
