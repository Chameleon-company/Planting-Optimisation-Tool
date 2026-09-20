import type { GeoJsonObject } from "geojson";
import { apiFetch } from "./apifetch";

export async function getFarmBoundary(farmId: number): Promise<GeoJsonObject> {
  const res = await apiFetch(`/farms/${farmId}/boundary`, {
    headers: {
      Accept: "application/json",
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch boundary");
  }

  return res.json();
}

export async function getPlantingGrid(farmId: number): Promise<GeoJsonObject> {
  const res = await apiFetch(`/sapling_estimation/${farmId}/grid`, {
    headers: {
      Accept: "application/json",
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch grid");
  }

  return res.json();
}
