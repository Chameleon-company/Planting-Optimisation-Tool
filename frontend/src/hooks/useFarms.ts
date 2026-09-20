import { useCallback, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiFetch } from "@/utils/apifetch";

// Mirrors the backend's FarmCreate, excluding id, riparian,
// and externally assigned ids.
export interface FarmCreatePayload {
  rainfall_mm: number;
  temperature_celsius: number;
  elevation_m: number;
  ph: number;
  soil_texture_id: number;
  area_ha: number;
  latitude: number;
  longitude: number;
  coastal: boolean;
  riparian: boolean;
  nitrogen_fixing: boolean;
  shade_tolerant: boolean;
  bank_stabilising: boolean;
  slope: number;
  agroforestry_type_ids: number[];
}

// Updating accepts a partial payload.
export type FarmUpdatePayload = Partial<FarmCreatePayload>;

export function useFarms() {
  const { user } = useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Create/POST farm.
  const createFarm = useCallback(
    async (payload: FarmCreatePayload): Promise<boolean> => {
      if (!user) {
        setError("You must be logged in to perform this action.");
        return false;
      }

      setIsLoading(true);
      setError(null);

      try {
        const res = await apiFetch("/farms", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!res.ok) {
          let message = "Failed to register farm";

          try {
            const err = await res.json();

            if (typeof err.detail === "string") {
              message = err.detail;
            }
          } catch {
            message = await res.text();
          }

          throw new Error(message);
        }

        return true;
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Unexpected error");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [user]
  );

  // Update/PUT farm.
  const updateFarm = useCallback(
    async (farmId: number, payload: FarmUpdatePayload): Promise<boolean> => {
      if (!user) {
        setError("You must be logged in to perform this action.");
        return false;
      }

      setIsLoading(true);
      setError(null);

      try {
        const res = await apiFetch(`/farms/${farmId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!res.ok) {
          let message = "Failed to update farm";

          try {
            const err = await res.json();

            if (typeof err.detail === "string") {
              message = err.detail;
            }
          } catch {
            message = await res.text();
          }

          throw new Error(message);
        }

        return true;
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Unexpected error");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [user]
  );

  // Delete farm.
  const deleteFarm = useCallback(
    async (farmId: number): Promise<boolean> => {
      if (!user) {
        setError("You must be logged in to perform this action.");
        return false;
      }

      setIsLoading(true);
      setError(null);

      try {
        const res = await apiFetch(`/farms/${farmId}`, {
          method: "DELETE",
          headers: {
            Accept: "application/json",
          },
        });

        if (!res.ok && res.status !== 204) {
          let message = "Failed to delete farm";

          try {
            const err = await res.json();

            if (typeof err.detail === "string") {
              message = err.detail;
            }
          } catch {
            message = await res.text();
          }

          throw new Error(message);
        }

        return true;
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Unexpected error");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [user]
  );

  return {
    isLoading,
    error,
    createFarm,
    updateFarm,
    deleteFarm,
  };
}
