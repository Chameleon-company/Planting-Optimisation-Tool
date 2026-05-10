import { useState, useEffect } from "react";
import type { GeoJsonObject } from "geojson";
import { useAuth } from "@/contexts/AuthContext";
import { getFarmBoundary, getPlantingGrid } from "@/utils/farmMapApi";

export interface FarmMapData {
  boundary: GeoJsonObject | null;
  grid: GeoJsonObject | null;
  isLoading: boolean;
  error: string | null;
}

export function useFarmMap(farmId: number | null): FarmMapData {
  const { getAccessToken } = useAuth();
  const [boundary, setBoundary] = useState<GeoJsonObject | null>(null);
  const [grid, setGrid] = useState<GeoJsonObject | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!farmId) return;

    const fetchMapData = async () => {
      setIsLoading(true);
      setError(null);
      setBoundary(null);
      setGrid(null);

      const token = getAccessToken();
      if (!token) {
        setError("Your session has expired. Please log in again.");
        setIsLoading(false);
        return;
      }

      const [boundaryResult, gridResult] = await Promise.allSettled([
        getFarmBoundary(farmId, token),
        getPlantingGrid(farmId, token),
      ]);

      if (boundaryResult.status === "fulfilled")
        setBoundary(boundaryResult.value);
      if (gridResult.status === "fulfilled") setGrid(gridResult.value);

      if (
        boundaryResult.status === "rejected" &&
        gridResult.status === "rejected"
      ) {
        setError("Failed to load map data.");
      }

      setIsLoading(false);
    };

    fetchMapData();
  }, [farmId, getAccessToken]);

  return { boundary, grid, isLoading, error };
}
