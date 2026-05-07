import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../contexts/AuthContext";

const API_BASE = import.meta.env.VITE_API_URL;

export interface SoilTexture {
  name: string;
}
export interface AgroforestryType {
  id: number;
  type_name: string;
}
export interface Farm {
  id: number;
  rainfall_mm: number;
  temperature_celsius: number;
  elevation_m: number;
  ph: number;
  soil_texture: SoilTexture;
  area_ha: number;
  latitude: number;
  longitude: number;
  coastal: boolean;
  riparian: boolean;
  nitrogen_fixing: boolean;
  shade_tolerant: boolean;
  bank_stabilising: boolean;
  slope: number;
  agroforestry_type: AgroforestryType[];
}

export function useUserProfiles() {
  const { getAccessToken } = useAuth();

  const [allFarms, setAllFarms] = useState<Farm[]>([]);
  const [page, setPage] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const PAGE_SIZE = 9;

  const token = getAccessToken();

  const fetchFarms = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setAllFarms([]);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/auth/users/me/items`, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || `Failed to fetch farms (${res.status})`);
      }

      const data: Farm[] = await res.json();
      const sorted = data.sort((a, b) => a.id - b.id);
      setAllFarms(sorted);
    } catch (err: unknown) {
      setAllFarms([]);
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
    } finally {
      setIsLoading(false);
    }
  }, [getAccessToken, token]);

  useEffect(() => {
    fetchFarms();
  }, [fetchFarms]);

  const farms = allFarms.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(allFarms.length / PAGE_SIZE);

  return {
    farms,
    isLoading,
    error,
    page,
    setPage,
    totalPages,
    totalFarms: allFarms.length,
    refetch: fetchFarms,
  };
}
