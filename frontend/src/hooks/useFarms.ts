import { useCallback, useState } from "react";
import { useAuth } from "../contexts/AuthContext";

const API_BASE = import.meta.env.VITE_API_URL;

// Mirrors the backend's FarmCreate, excluding id, riparian, and externally assigned id's
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

// Updating accepts a partial payload
export type FarmUpdatePayload = Partial<FarmCreatePayload>;

export function useFarms() {
  const { getAccessToken } = useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Create/POST farms, for admins only
  const createFarm = useCallback(
    // Async, with a FarmCreatePayload, promising a function with a boolean end result
    async (payload: FarmCreatePayload): Promise<boolean> => {
      const token = getAccessToken();
      if (!token) {
        setError("You must be logged in to perform this action.");
        return false;
      }

      setIsLoading(true);
      setError(null);

      // Try/Catch, using post, calling the API, handing payload as JSON package
      try {
        const res = await fetch(`${API_BASE}/farms`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify(payload),
        });

        // Error handling
        if (!res.ok) {
          let message = "Failed to register farm";
          try {
            const err = await res.json();
            if (typeof err.detail === "string") message = err.detail;
          } catch {
            message = await res.text();
          }
          throw new Error(message);
        }

        // IF no error returned, return true
        return true;
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Unexpected error");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    // Refetch when getToken is called
    [getAccessToken]
  );

  // Update/PUT, admins any farm, supervisors only their own
  const updateFarm = useCallback(
    // Same async, requring at least partial payload and a farmID
    async (farmId: number, payload: FarmUpdatePayload): Promise<boolean> => {
      const token = getAccessToken();
      if (!token) {
        setError("You must be logged in to perform this action.");
        return false;
      }

      setIsLoading(true);
      setError(null);

      // Try/catch, JSON-ify payload, fetching API update call using farmID
      try {
        const res = await fetch(`${API_BASE}/farms/${farmId}`, {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!res.ok) {
          let message = "Failed to update farm";
          try {
            const err = await res.json();
            if (typeof err.detail === "string") message = err.detail;
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
    [getAccessToken]
  );

  // Delete/DELETE, admins only, responds with 204 No Content on success
  const deleteFarm = useCallback(
    async (farmId: number): Promise<boolean> => {
      const token = getAccessToken();
      if (!token) {
        setError("You must be logged in to perform this action.");
        return false;
      }

      setIsLoading(true);
      setError(null);

      // Call delte API call, using farmID
      try {
        const res = await fetch(`${API_BASE}/farms/${farmId}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/json",
          },
        });

        // 204 No Content is the successful response, if not respond with this, error
        if (!res.ok && res.status !== 204) {
          let message = "Failed to delete farm";
          try {
            const err = await res.json();
            if (typeof err.detail === "string") message = err.detail;
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
    [getAccessToken]
  );

  return { isLoading, error, createFarm, updateFarm, deleteFarm };
}
