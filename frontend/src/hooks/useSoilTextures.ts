import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL;

interface SoilTexture {
  id: number;
  name: string;
}

export function useSoilTextures() {
  const [soilTextures, setSoilTextures] = useState<SoilTexture[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    setIsLoading(true);
    setError(null);

    fetch(`${API_BASE}/soil-textures`)
      .then(res => {
        // Check res.ok before attempting to parse, so error bodies
        // don't get silently set as valid
        if (!res.ok) {
          throw new Error(`Failed to load soil textures (${res.status})`);
        }
        return res.json();
      })
      .then((data: SoilTexture[]) => {
        if (!cancelled) setSoilTextures(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unexpected error");
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { soilTextures, isLoading, error };
}
