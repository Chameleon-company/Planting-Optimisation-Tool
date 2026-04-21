import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";

const API_BASE = import.meta.env.VITE_API_URL;

export interface SoilTexture {
  name: string;
}
export interface AgroforestryType {
  name: string;
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
  const token = getAccessToken();

  const [allFarms, setAllFarms] = useState<Farm[]>([]);
  const [page, setPage] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const PAGE_SIZE = 9;

  useEffect(() => {
    if (!token) {
      setError(null);
      return;
    }

    const fetchFarms = async () => {
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

        const data = await res.json();
        setAllFarms(data);
      } catch (err: unknown) {
        setAllFarms([]);
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("An unexpected error occurred");
        }
      } finally {
        setIsLoading(false);
      }
    };
    fetchFarms();
  }, [token]);

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
  };
}
