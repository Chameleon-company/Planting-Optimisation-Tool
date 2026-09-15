import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { Farm } from "./useUserProfiles";

const API_BASE = import.meta.env.VITE_API_URL;

export function useSearchProfiles(query: string) {
  const { getAccessToken } = useAuth();
  const token = getAccessToken();

  const [profile, setProfile] = useState<Farm | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    if (!query.trim() || !token) {
      setProfile(null);
      setError(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/farms/${query}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      });

      if (!res.ok) {
        let errorMessage = "Something went wrong";

        try {
          const errorData = await res.json();

          if (typeof errorData.detail === "string") {
            errorMessage = errorData.detail;
          }
        } catch {
          errorMessage = `Failed to load profile (${res.status})`;
        }

        throw new Error(errorMessage);
      }

      const data: Farm = await res.json();

      setProfile({
        ...data,
        id: data.id ?? Number(query),
      });
    } catch (err: unknown) {
      setProfile(null);
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setIsLoading(false);
    }
  }, [query, token]);

  useEffect(() => {
    void fetchProfile();
  }, [fetchProfile]);

  const replaceProfile = useCallback((nextProfile: Farm) => {
    setProfile(nextProfile);
    setError(null);
  }, []);

  return {
    profile,
    isLoading,
    error,
    refetch: fetchProfile,
    replaceProfile,
  };
}
