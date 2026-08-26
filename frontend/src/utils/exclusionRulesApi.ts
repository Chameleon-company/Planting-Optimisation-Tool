const API_BASE = import.meta.env.VITE_API_URL;

// ---------- TYPES ----------

export type ExclusionOperator =
  | "<"
  | ">"
  | "<="
  | ">="
  | "=="
  | "!="
  | "in_set"
  | "not_in_set";

export type ExclusionRuleValue = number | string | string[];

export interface ExclusionRule {
  id: number;
  species_id: number;
  feature: string;
  operator: ExclusionOperator;
  value: ExclusionRuleValue;
  reason: string;
}

export interface ExclusionRulePayload {
  species_id: number;
  feature: string;
  operator: ExclusionOperator;
  value: ExclusionRuleValue;
  reason: string;
}

export interface ExclusionRuleUpdatePayload {
  species_id?: number;
  feature?: string;
  operator?: ExclusionOperator;
  value?: ExclusionRuleValue;
  reason?: string;
}

export interface SpeciesDependency {
  id: number;
  focal_species_id: number;
  required_partner_id: number;
}

export interface SpeciesDependencyPayload {
  focal_species_id: number;
  required_partner_id: number;
}

export interface SpeciesDependencyUpdatePayload {
  focal_species_id?: number;
  required_partner_id?: number;
}

// ---------- HELPERS ----------

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

        return "Invalid rule data.";
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

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const error = await res.json();
    throw new Error(formatApiError(error));
  }

  return res.json() as Promise<T>;
}

async function handleDeleteResponse(res: Response): Promise<void> {
  if (!res.ok) {
    const error = await res.json();
    throw new Error(formatApiError(error));
  }
}

// ---------- EXCLUSION RULES ----------

export async function getAllExclusionRules(
  token: string
): Promise<ExclusionRule[]> {
  const res = await fetch(`${API_BASE}/exclusion-rules`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse<ExclusionRule[]>(res);
}

export async function getExclusionRuleById(
  id: number,
  token: string
): Promise<ExclusionRule> {
  const res = await fetch(`${API_BASE}/exclusion-rules/${id}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse<ExclusionRule>(res);
}

export async function createExclusionRule(
  data: ExclusionRulePayload,
  token: string
): Promise<ExclusionRule> {
  const res = await fetch(`${API_BASE}/exclusion-rules`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleResponse<ExclusionRule>(res);
}

export async function updateExclusionRule(
  id: number,
  data: ExclusionRuleUpdatePayload,
  token: string
): Promise<ExclusionRule> {
  const res = await fetch(`${API_BASE}/exclusion-rules/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleResponse<ExclusionRule>(res);
}

export async function deleteExclusionRule(
  id: number,
  token: string
): Promise<void> {
  const res = await fetch(`${API_BASE}/exclusion-rules/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleDeleteResponse(res);
}

// ---------- SPECIES DEPENDENCIES ----------

export async function getAllDependencies(
  token: string
): Promise<SpeciesDependency[]> {
  const res = await fetch(`${API_BASE}/species-dependencies`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse<SpeciesDependency[]>(res);
}

export async function getDependencyById(
  id: number,
  token: string
): Promise<SpeciesDependency> {
  const res = await fetch(`${API_BASE}/species-dependencies/${id}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse<SpeciesDependency>(res);
}

export async function createDependency(
  data: SpeciesDependencyPayload,
  token: string
): Promise<SpeciesDependency> {
  const res = await fetch(`${API_BASE}/species-dependencies`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleResponse<SpeciesDependency>(res);
}

export async function updateDependency(
  id: number,
  data: SpeciesDependencyUpdatePayload,
  token: string
): Promise<SpeciesDependency> {
  const res = await fetch(`${API_BASE}/species-dependencies/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleResponse<SpeciesDependency>(res);
}

export async function deleteDependency(
  id: number,
  token: string
): Promise<void> {
  const res = await fetch(`${API_BASE}/species-dependencies/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleDeleteResponse(res);
}
