import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";

const API_BASE = import.meta.env.VITE_API_URL;

export interface CalculatorResult {
  id: number;
  pre_slope_count: number;
  aligned_count: number;
  optimal_angle: number;
}

export function useCalculator(farmId: string) {
  const { getAccessToken } = useAuth();
  const [result, setResult] = useState<CalculatorResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!farmId) return;

    const fetchEstimation = async () => {
      setIsLoading(true);
      setError(null);
      setHasSearched(false);
      setResult(null);

      const token = getAccessToken();
      if (!token) {
        setError("Your session has expired. Please log in again.");
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `${API_BASE}/sapling_estimation/calculate`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              farm_id: Number(farmId),
              spacing_x: 3.0,
              spacing_y: 3.0,
              max_slope: 15.0,
            }),
          }
        );

        if (!response.ok) {
          const data = await response.json();
          setError(data.message || "Failed to fetch estimation");
          setIsLoading(false);
          return;
        }

        const data = await response.json();
        setResult(data);
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

    fetchEstimation();
  }, [farmId, getAccessToken]);

  return { result, isLoading, hasSearched, error };
}
