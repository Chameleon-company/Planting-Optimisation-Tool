import { useState, useEffect } from "react";
import { apiFetch } from "../utils/apiFetch";

export interface Recommendation {
  species_id: number;
  rank_overall: number;
  species_common_name: string;
  species_name: string;
  score_mcda: number;
  key_reasons: string[];
}

export interface ExcludedSpecies {
  id: number;
  species_common_name: string;
  species_name: string;
  reasons: string[];
}

export function useRecommendations(farmId: string) {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [excludes, setExcludes] = useState<ExcludedSpecies[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!farmId) return;

    const fetchRecs = async () => {
      setIsLoading(true);
      setError(null);
      setHasSearched(false);
      setRecs([]);
      setExcludes([]);

      try {
        const response = await apiFetch(`/recommendations/${farmId}`, {
          method: "GET",
          headers: {
            Accept: "application/json",
          },
        });

        if (!response.ok) {
          const errorData = await response.json();

          throw new Error(
            errorData.detail || "Failed to fetch recommendations"
          );
        }

        const data = await response.json();

        setRecs(data.recommendations || []);
        setExcludes(data.excluded_species || []);
        setHasSearched(true);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("An unexpected error occurred");
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecs();
  }, [farmId]);

  // Triggers the PDF generation and download from the reporting service.
  const downloadPdf = async () => {
    if (!farmId) return;

    try {
      const response = await apiFetch(`/reports/farm/${farmId}/export/pdf`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error("Failed to generate PDF");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `farm_${farmId}_report.pdf`;

      document.body.appendChild(a);
      a.click();

      window.URL.revokeObjectURL(url);
      a.remove();
    } catch {
      setError("Error downloading PDF report.");
    }
  };

  return {
    recs,
    excludes,
    isLoading,
    hasSearched,
    error,
    downloadPdf,
  };
}
