import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getSaplingEstimation } from "@/utils/calculatorApi";
import type { CalcParams, FarmEstimationResult } from "@/utils/calculatorApi";

export type { CalcParams, FarmEstimationResult };

export const DEFAULT_CALC_PARAMS: CalcParams = {
  spacingX: 3.0,
  spacingY: 3.0,
  maxSlope: 15.0,
};

export function useCalculator(farmIds: number[], params: CalcParams) {
  const { getAccessToken } = useAuth();
  const [results, setResults] = useState<FarmEstimationResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!farmIds.length) return;
    let active = true;

    const fetchEstimation = async () => {
      setIsLoading(true);
      setError(null);
      setHasSearched(false);
      setResults([]);

      const token = getAccessToken();
      if (!token) {
        if (active) {
          setError("Please log in to continue.");
          setIsLoading(false);
        }
        return;
      }

      try {
        const data = await getSaplingEstimation(farmIds, params, token);
        if (!active) return;
        setResults(data.results);
        setHasSearched(true);
      } catch (err: unknown) {
        if (!active) return;
        setError(
          err instanceof Error ? err.message : "An unexpected error occurred"
        );
      } finally {
        if (active) setIsLoading(false);
      }
    };

    fetchEstimation();
    return () => {
      active = false;
    };
  }, [farmIds, params, getAccessToken]);

  return { results, isLoading, hasSearched, error };
}
