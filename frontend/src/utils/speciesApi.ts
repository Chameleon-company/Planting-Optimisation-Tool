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
    throw new Error(formatApiError(error));
  }
  return res.json();
}

function formatFieldName(field: string): string {
  const base = field
    .replace("response.", "")
    .replace("body.", "")
    .split("_")[0];

  if (base.toLowerCase() === "ph") {
    return "pH";
  }

  return base.replace(/\b\w/g, char => char.toUpperCase());
}

function formatApiError(error: unknown): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "detail" in error &&
    Array.isArray(error.detail)
  ) {
    return error.detail
      .map(item => {
        if (typeof item === "object" && item !== null) {
          const field =
            "field" in item && typeof item.field === "string"
              ? formatFieldName(item.field)
              : "";

          if ("msg" in item && typeof item.msg === "string") {
            return field ? `${field}: ${item.msg}` : item.msg;
          }

          if ("message" in item && typeof item.message === "string") {
            return field ? `${field}: ${item.message}` : item.message;
          }
        }

        return "Invalid species data.";
      })
      .join(" ");
  }

  if (
    typeof error === "object" &&
    error !== null &&
    "detail" in error &&
    typeof error.detail === "string"
  ) {
    return error.detail;
  }

  return "API error";
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
