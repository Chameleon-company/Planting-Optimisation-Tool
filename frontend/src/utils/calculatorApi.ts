import { apiFetch } from "./apifetch";

export interface CalcParams {
  spacingX: number;
  spacingY: number;
  maxSlope: number;
}

export interface CalculatorResult {
  id: number;
  pre_slope_count: number;
  aligned_count: number;
  optimal_angle: number;
}

export async function getSaplingEstimation(
  farmId: number,
  params: CalcParams
): Promise<CalculatorResult> {
  const res = await apiFetch("/sapling_estimation/calculate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      farm_id: farmId,
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
