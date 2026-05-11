import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { Farm } from "./useUserProfiles";

const API_BASE = import.meta.env.VITE_API_URL;

export function useSearchProfiles(query: string) {
  const { getAccessToken } = useAuth();
  const token = getAccessToken();

  const [profile, setProfile] = useState<Farm | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query.trim() || !token) {
      setProfile(null);
      setError(null);
      return;
    }

    const fetchProfile = async () => {
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
            errorMessage = await res.text();
          }
          throw new Error(errorMessage);
        }

        const data = await res.json();
        data.id = data.id ?? Number(query);
        setProfile(data);
      } catch (err: unknown) {
        setProfile(null);
        setError(err instanceof Error ? err.message : "Unexpected error");
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [query, token]);

  return { profile, isLoading, error };
}
