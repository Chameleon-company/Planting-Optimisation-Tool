const API_BASE = import.meta.env.VITE_API_URL;

export interface CalcParams {
  spacingX: number;
  spacingY: number;
  maxSlope: number;
}

export interface FarmEstimationResult {
  farm_id: number;
  status: "success" | "failed";
  message?: string | null;
  pre_slope_count?: number | null;
  aligned_count?: number | null;
  optimal_angle?: number | null;
  rotation_average?: number | null;
  rotation_std_dev?: number | null;
}

export interface SaplingEstimationResponse {
  status: string;
  farm_count: number;
  results: FarmEstimationResult[];
}

export async function getSaplingEstimation(
  farmIds: number[],
  params: CalcParams,
  token: string
): Promise<SaplingEstimationResponse> {
  const res = await fetch(`${API_BASE}/sapling_estimation/calculate`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      farm_ids: farmIds,
      spacing_x: params.spacingX,
      spacing_y: params.spacingY,
      max_slope: params.maxSlope,
    }),
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || "Failed to fetch estimation");
  }
  return res.json();
}
