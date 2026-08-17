const API_BASE = import.meta.env.VITE_API_URL;

// ---------- TYPES ----------

export interface Parameter {
  id: number;
  species_id: number;
  feature: string;
  score_method: string | null;
  weight: number | null;
  trap_left_tol: number | null;
  trap_right_tol: number | null;
}

export interface ParameterPayload {
  species_id: number;
  feature: string;
  score_method: string;
  weight: number;
  trap_left_tol: number | null;
  trap_right_tol: number | null;
}

export interface ParameterUpdatePayload {
  species_id?: number;
  feature?: string;
  score_method?: string;
  weight?: number;
  trap_left_tol?: number | null;
  trap_right_tol?: number | null;
}

// ---------- HELPERS ----------

async function handleResponse(res: Response) {
  if (!res.ok) {
    const error = await res.json();
    throw new Error(formatApiError(error));
  }
  return res.json();
}

function formatApiError(error: unknown): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "detail" in error &&
    Array.isArray(error.detail)
  ) {
    return error.detail
      .map((item: unknown) => {
        if (typeof item === "object" && item !== null) {
          if ("msg" in item && typeof item.msg === "string") {
            return item.msg;
          }
          if ("message" in item && typeof item.message === "string") {
            return item.message;
          }
        }
        return "Invalid parameter data.";
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

// ---------- PARAMETERS ----------

export async function getAllParameters(token: string): Promise<Parameter[]> {
  const res = await fetch(`${API_BASE}/parameters`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse(res);
}

export async function getParametersBySpecies(
  speciesId: number,
  token: string
): Promise<Parameter[]> {
  const res = await fetch(`${API_BASE}/parameters/species/${speciesId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse(res);
}

export async function createParameter(
  data: ParameterPayload,
  token: string
): Promise<Parameter> {
  const res = await fetch(`${API_BASE}/parameters`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleResponse(res);
}

export async function updateParameter(
  id: number,
  data: ParameterUpdatePayload,
  token: string
): Promise<Parameter> {
  const res = await fetch(`${API_BASE}/parameters/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleResponse(res);
}

export async function deleteParameter(
  id: number,
  token: string
): Promise<void> {
  const res = await fetch(`${API_BASE}/parameters/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(formatApiError(error));
  }
}
