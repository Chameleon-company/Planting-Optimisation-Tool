import type { GeoJsonObject } from "geojson";

const API_BASE = import.meta.env.VITE_API_URL;

export async function getFarmBoundary(
  farmId: number,
  token: string
): Promise<GeoJsonObject> {
  const res = await fetch(`${API_BASE}/farms/${farmId}/boundary`, {
    headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
  });
  if (!res.ok) throw new Error("Failed to fetch boundary");
  return res.json();
}

export async function getPlantingGrid(
  farmId: number,
  token: string
): Promise<GeoJsonObject> {
  const res = await fetch(`${API_BASE}/sapling_estimation/${farmId}/grid`, {
    headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
  });
  if (!res.ok) throw new Error("Failed to fetch grid");
  return res.json();
}
