import { useCallback, useState } from "react";
import { useAuth } from "../contexts/AuthContext";

const API_BASE = import.meta.env.VITE_API_URL;

export interface RegeneratedProfile {
  id?: number;
  status: string;
  data_source?: string;
  rainfall_mm?: number;
  temperature_celsius?: number;
  elevation_m?: number;
  ph?: number;
  slope?: number;
  soil_texture_id?: number;
  soil_texture?: string;
  area_ha?: number;
  latitude?: number;
  longitude?: number;
  coastal?: boolean;
  riparian?: boolean;
  nitrogen_fixing?: boolean;
  shade_tolerant?: boolean;
  bank_stabilising?: boolean;
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const data = await response.json();

    if (typeof data.detail === "string") {
      return data.detail;
    }
  } catch {
    // Use the fallback message when the response is not JSON.
  }

  return `Request failed (${response.status})`;
}

export function useProfileActions() {
  const { getAccessToken } = useAuth();

  const [isRegenerating, setIsRegenerating] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const clearActionFeedback = useCallback(() => {
    setActionError(null);
    setActionMessage(null);
  }, []);

  const regenerateProfile = useCallback(
    async (farmId: number): Promise<RegeneratedProfile> => {
      const token = getAccessToken();

      if (!token) {
        const message = "You must be logged in.";
        setActionError(message);
        throw new Error(message);
      }

      setIsRegenerating(true);
      setActionError(null);
      setActionMessage(null);

      try {
        const response = await fetch(
          `${API_BASE}/profile/${farmId}/regenerate`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
              Accept: "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(await getErrorMessage(response));
        }

        const regeneratedProfile: RegeneratedProfile = await response.json();

        setActionMessage("Environmental profile regenerated successfully.");

        return regeneratedProfile;
      } catch (error: unknown) {
        const message =
          error instanceof Error
            ? error.message
            : "Failed to regenerate the environmental profile.";

        setActionError(message);
        throw new Error(message);
      } finally {
        setIsRegenerating(false);
      }
    },
    [getAccessToken]
  );

  return {
    regenerateProfile,
    isRegenerating,
    actionError,
    actionMessage,
    clearActionFeedback,
  };
}
