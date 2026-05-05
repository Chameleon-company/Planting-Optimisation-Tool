// Mirrored from the backend's AgroforestryTypeID
// To be deleted when agrofor endpoint is added
export const AGROFORESTRY_TYPE_OPTIONS = [
  { id: 1, name: "Block" },
  { id: 2, name: "Boundary" },
  { id: 3, name: "Intercropping" },
  { id: 4, name: "Mosaic" },
];

// Interface for modal's set form use state
export interface FormState {
  rainfall_mm: string;
  temperature_celsius: string;
  elevation_m: string;
  ph: string;
  soil_texture_id: string;
  area_ha: string;
  latitude: string;
  longitude: string;
  coastal: boolean;
  nitrogen_fixing: boolean;
  shade_tolerant: boolean;
  bank_stabilising: boolean;
  slope: string;
  agroforestry_type_ids: number[];
}

// Interface for modal's use state error's
export interface FormErrors {
  rainfall_mm?: string;
  temperature_celsius?: string;
  elevation_m?: string;
  ph?: string;
  soil_texture_id?: string;
  area_ha?: string;
  latitude?: string;
  longitude?: string;
  slope?: string;
  agroforestry_type_ids?: string;
}
