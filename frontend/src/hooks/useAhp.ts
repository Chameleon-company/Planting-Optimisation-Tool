import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { AhpResponse, CalculationRequest } from "@/utils/ahp_types";

const API_BASE = import.meta.env.VITE_API_URL;

// --- TYPES ---
export interface SpeciesDropdownItem {
  id: number;
  name: string;
  common_name: string;
}

export interface FactorsResponse {
  factors: string[];
}

// --- SPECIES DROPDOWN HOOK ---
export function useAhpSpecies() {
  const { getAccessToken } = useAuth();
  const [speciesList, setSpeciesList] = useState<SpeciesDropdownItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSpecies = async () => {
      const token = getAccessToken();
      setIsLoading(true);
      setError(null);

      if (!token) {
        setError("Your session has expired. Please log in again.");
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(`${API_BASE}/species/dropdown`, {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch species: ${response.statusText}`);
        }

        const data: SpeciesDropdownItem[] = await response.json();
        setSpeciesList(data);
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

    fetchSpecies();
  }, [getAccessToken]);

  return { speciesList, isLoading, error };
}

// --- AHP CONFIG (FEATURES) HOOK ---
export function useAhpFactors() {
  const { getAccessToken } = useAuth();
  const [factorsList, setFactorsList] = useState<FactorsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFactors = async () => {
      const token = getAccessToken();
      setIsLoading(true);
      setError(null);

      if (!token) {
        setError("Your session has expired. Please log in again.");
        setIsLoading(false);
        return;
      }

      try {
        const headers: HeadersInit = { Accept: "application/json" };
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const response = await fetch(`${API_BASE}/species/features`, {
          method: "GET",
          headers,
        });
        if (!response.ok) {
          throw new Error(`Could not load features: ${response.statusText}`);
        }

        const rawData: string[] = await response.json();
        setFactorsList({ factors: rawData });
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

    fetchFactors();
  }, [getAccessToken]);

  return { factorsList, isLoading, error };
}

// --- AHP CALCULATION HOOK ---
export function useAhpCalculation() {
  const { getAccessToken } = useAuth();
  const [results, setResults] = useState<AhpResponse | null>(null);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleCalculate = async (payload: CalculationRequest) => {
    const token = getAccessToken();
    setIsCalculating(true);
    setError(null);

    if (!token) {
      setError("Your session has expired. Please log in again.");
      setIsCalculating(false);
      return;
    }

    try {
      const headers: HeadersInit = {
        "Content-Type": "application/json",
        Accept: "application/json",
      };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const response = await fetch(`${API_BASE}/ahp/calculate-and-save`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let errorMessage = "Invalid matrix payload.";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          errorMessage = response.statusText;
        }
        throw new Error(`Calculation failed: ${errorMessage}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(msg);
    } finally {
      setIsCalculating(false);
    }
  };

  const resetCalculation = () => {
    setResults(null);
    setError(null);
  };

  return { results, isCalculating, handleCalculate, resetCalculation, error };
}
