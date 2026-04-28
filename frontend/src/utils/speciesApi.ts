const API_BASE = import.meta.env.VITE_API_URL;

// ---------- TYPES ----------

export interface SoilTexture {
  id: number;
  name: string;
}

export interface AgroforestryType {
  id: number;
  type_name: string;
}

export interface Species {
  id: number;
  name: string;
  common_name: string;
  rainfall_mm_min: number;
  rainfall_mm_max: number;
  temperature_celsius_min: number;
  temperature_celsius_max: number;
  elevation_m_min: number;
  elevation_m_max: number;
  ph_min: number;
  ph_max: number;
  coastal: boolean;
  riparian: boolean;
  nitrogen_fixing: boolean;
  shade_tolerant: boolean;
  bank_stabilising: boolean;
  soil_textures: SoilTexture[];
  agroforestry_types: AgroforestryType[];
}

// Payload for create/update
export interface SpeciesPayload {
  name: string;
  common_name: string;
  rainfall_mm_min: number;
  rainfall_mm_max: number;
  temperature_celsius_min: number;
  temperature_celsius_max: number;
  elevation_m_min: number;
  elevation_m_max: number;
  ph_min: number;
  ph_max: number;
  coastal: boolean;
  riparian: boolean;
  nitrogen_fixing: boolean;
  shade_tolerant: boolean;
  bank_stabilising: boolean;
  soil_textures: number[];
  agroforestry_types: number[];
}

// ---------- HELPERS ----------

async function handleResponse(res: Response) {
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "API error");
  }
  return res.json();
}

// ---------- SPECIES ----------

export async function getAllSpecies(token: string): Promise<Species[]> {
  const res = await fetch(`${API_BASE}/species`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse(res);
}

export async function getSpeciesById(
  id: number,
  token: string
): Promise<Species> {
  const res = await fetch(`${API_BASE}/species/${id}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse(res);
}

export async function createSpecies(
  data: SpeciesPayload,
  token: string
): Promise<Species> {
  const res = await fetch(`${API_BASE}/species`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleResponse(res);
}

export async function updateSpecies(
  id: number,
  data: SpeciesPayload,
  token: string
): Promise<Species> {
  const res = await fetch(`${API_BASE}/species/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleResponse(res);
}

export async function deleteSpecies(id: number, token: string): Promise<void> {
  const res = await fetch(`${API_BASE}/species/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Delete failed");
  }
}

// ---------- OPTIONS ----------

export async function getSoilTextures(): Promise<SoilTexture[]> {
  const res = await fetch(`${API_BASE}/soil-textures`);
  return handleResponse(res);
}
