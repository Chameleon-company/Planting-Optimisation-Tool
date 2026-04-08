import { useState } from "react";
import { Species } from "../utils/contentfulClient";
import { useSpecies } from "../hooks/useSpecies";
import { Helmet } from "react-helmet-async";

import SpeciesGrid from "@/components/species/speciesGrid";
import SpeciesModal from "@/components/species/speciesModal";
import SpeciesHeader from "@/components/species/speciesHeader";
import SpeciesSearch from "@/components/species/speciesSearch";

export default function SpeciesPage() {
  // Set query as useState, capable of being changed by setQuery
  const [query, setQuery] = useState("");
  // Set selectedSpecies as useState, capable of being changed by setSelectedSpecies, of state Species or null, default null
  const [selectedSpecies, setSelectedSpecies] = useState<Species | null>(null);
  // Set species, isLoading and error as const, gathered from useSpecies being handed query
  const { species, isLoading, error } = useSpecies(query);

  return (
    <div>
      <Helmet>
        <title>Species | Planting Optimisation Tool</title>
      </Helmet>

      <SpeciesHeader />

      {/* Search bar, updates setQuery and thus query when onSearch called in SpeciesSearch */}
      <SpeciesSearch onSearch={setQuery} isLoading={isLoading} />

      {/* Error log, states search error if one appears */}
      {error && <p className="species-empty">{error}</p>}

      {/* SpeciesGrid, creates grid of searched species array, on card click, set that as SelectedSpecies */}
      <SpeciesGrid species={species} onCardClick={setSelectedSpecies} />

      {/* SpeciesModal, hand selectedSpecies, when closed, setSelectedSpecies to null */}
      <SpeciesModal
        item={selectedSpecies}
        onClose={() => setSelectedSpecies(null)}
      />
    </div>
  );
}
