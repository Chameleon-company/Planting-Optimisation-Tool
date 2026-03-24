import { useState, useEffect } from "react";
import { client, Species } from "../utils/contentfulClient";

export function useSpecies(query: string = "") {
  // Set species as a useState, with a type of interface Species[] from Contentful, default is empty
  const [species, setSpecies] = useState<Species[]>([]);
  // Set isLoading as a useState, default is false
  const [isLoading, setIsLoading] = useState(false);
  // Set error as a useState, of type string or null, default is null
  const [error, setError] = useState<string | null>(null);

  // useEffect, to call on initialisation or when the query variable has changed
  // Effectively this causes fetchSpecies to trigger when enter or the search button is pressed
  useEffect(() => {
    // Create async fetchSpecies function inside useEffect
    async function fetchSpecies() {
      setIsLoading(true);
      setError(null);
      // Try/Catch awaiting response from Contentful client calling .getEntries, with query set to the users query
      try {
        const response = await client.getEntries({
          content_type: "species",
          query: query,
          limit: 100,
        });
        setSpecies(response.items as unknown as Species[]);
      } catch (err) {
        console.error("Error fetching species:", err);
        setError("Failed to fetch species.");
      } finally {
        setIsLoading(false);
      }
    }

    // Call fetchSpecies once query is updated.
    fetchSpecies();
  }, [query]);

  // return species array containg article cards, isLoading, and error to SpeciesPage
  return { species, isLoading, error };
}
