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

    let cancelled = false;

    const fetchBoundary = async () => {
      setIsLoading(true);
      setError(null);
      setBoundary(null);

      const token = getAccessToken();
      if (!token) {
        if (!cancelled) {
          setError("Please log in to continue.");
          setIsLoading(false);
        }
        return;
      }

      try {
        const data = await getFarmBoundary(farmId, token);
        if (!cancelled) {
          setBoundary(data);
        }
      } catch {
        if (!cancelled) {
          setError("Failed to load farm boundary.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    fetchBoundary();

    return () => {
      cancelled = true;
    };
  }, [farmId, getAccessToken]);

  return { boundary, isLoading, error };
}
