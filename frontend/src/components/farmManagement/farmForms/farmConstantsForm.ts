// Mirrored from the backend's SoilTextureID
export const SOIL_TEXTURE_OPTIONS = [
  { id: 1, label: "Sand" },
  { id: 2, label: "Loamy sand" },
  { id: 3, label: "Sandy loam" },
  { id: 4, label: "Loam" },
  { id: 5, label: "Silty loam" },
  { id: 6, label: "Silt" },
  { id: 7, label: "Sandy clay loam" },
  { id: 8, label: "Clay loam" },
  { id: 9, label: "Silty clay loam" },
  { id: 10, label: "Sandy clay" },
  { id: 11, label: "Silty clay" },
  { id: 12, label: "Clay" },
];

// Mirrored from the backend's AgroforestryTypeID
export const AGROFORESTRY_TYPE_OPTIONS = [
  { id: 1, label: "Block" },
  { id: 2, label: "Boundary" },
  { id: 3, label: "Intercropping" },
  { id: 4, label: "Mosaic" },
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
