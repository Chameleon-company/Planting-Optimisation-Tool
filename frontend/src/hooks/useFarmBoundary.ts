import { useState, useEffect } from "react";
import type { GeoJsonObject } from "geojson";
import { useAuth } from "@/contexts/AuthContext";
import { getFarmBoundary } from "@/utils/farmMapApi";

export interface FarmBoundaryData {
  boundary: GeoJsonObject | null;
  isLoading: boolean;
  error: string | null;
}

export function useFarmBoundary(farmId: number | null): FarmBoundaryData {
  const { getAccessToken } = useAuth();
  const [boundary, setBoundary] = useState<GeoJsonObject | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!farmId) {
      setBoundary(null);
      setError(null);
      return;
    }

    const fetchBoundary = async () => {
      setIsLoading(true);
      setError(null);
      setBoundary(null);

      const token = getAccessToken();
      if (!token) {
        setError("Please log in to continue.");
        setIsLoading(false);
        return;
      }

      try {
        const data = await getFarmBoundary(farmId, token);
        setBoundary(data);
      } catch {
        setError("Failed to load farm boundary.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchBoundary();
  }, [farmId, getAccessToken]);

  return { boundary, isLoading, error };
}
