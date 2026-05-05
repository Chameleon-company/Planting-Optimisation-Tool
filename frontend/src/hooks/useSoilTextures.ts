import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL;

interface SoilTexture {
  id: number;
  name: string;
}

export function useSoilTextures() {
  const [soilTextures, setSoilTextures] = useState<SoilTexture[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/soil-textures`)
      .then(res => res.json())
      .then(data => setSoilTextures(data))
      .finally(() => setIsLoading(false));
  }, []);

  return { soilTextures, isLoading };
}
