import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getSaplingEstimation } from "@/utils/calculatorApi";
import type { CalcParams, CalculatorResult } from "@/utils/calculatorApi";

export type { CalcParams, CalculatorResult };

export const DEFAULT_CALC_PARAMS: CalcParams = {
  spacingX: 3.0,
  spacingY: 3.0,
  maxSlope: 15.0,
};

export function useCalculator(farmId: string, params: CalcParams) {
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
        const data = await getSaplingEstimation(Number(farmId), params, token);
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
  }, [farmId, params, getAccessToken]);

  return { result, isLoading, hasSearched, error };
}
