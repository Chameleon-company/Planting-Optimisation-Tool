export interface CalculationRequest {
  species_id: number;
  matrix: number[][]; // N x N array of floats
}

export interface AhpResponse {
  weights: Record<string, number>; // e.g., { "Rainfall": 0.264, "Elevation": 0.081 }
  consistency_ratio: number;
  is_consistent: boolean;
  message: string;
}
