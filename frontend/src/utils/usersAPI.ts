const API_BASE = import.meta.env.VITE_API_URL;

const USERS_PATH = "/users";

// ---------- TYPES ----------

export type Role = "officer" | "supervisor" | "admin";
export const ROLES: Role[] = ["officer", "supervisor", "admin"];

export const ROLE_LABELS: Record<Role, string> = {
  officer: "Officer",
  supervisor: "Supervisor",
  admin: "Admin",
};

export interface UserRead {
  id: number;
  email: string;
  name: string;
  role: Role;
  is_approved: boolean;
  requested_role: Role | null;
}

export interface UserCreate {
  email: string;
  name: string;
  password: string;
  role?: Role;
}

export interface UserUpdate {
  email?: string;
  name?: string;
  password?: string;
  role?: Role;
}

// ---------- HELPERS ----------

async function extractError(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((item: { msg?: string }) => item.msg || "Invalid input")
        .join(", ");
    }
  } catch {
    // body wasn't JSON
  }
  return fallback;
}

function authHeaders(token: string, json = false): Record<string, string> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
    Accept: "application/json",
  };
  if (json) headers["Content-Type"] = "application/json";
  return headers;
}

// ---------- USERS (admin / supervisor) ----------

export async function listUsers(
  token: string,
  skip = 0,
  limit = 100
): Promise<UserRead[]> {
  const res = await fetch(
    `${API_BASE}${USERS_PATH}/?skip=${skip}&limit=${limit}`,
    { headers: authHeaders(token) }
  );
  if (!res.ok) {
    throw new Error(
      await extractError(res, `Failed to fetch users (${res.status})`)
    );
  }
  return res.json();
}

// GET /users/pending - ADMIN only Non-admins get 403, so only call this
// when you know the caller is an admin
export async function listPending(token: string): Promise<UserRead[]> {
  const res = await fetch(`${API_BASE}${USERS_PATH}/pending`, {
    headers: authHeaders(token),
  });
  if (!res.ok) {
    throw new Error(
      await extractError(res, `Failed to fetch pending users (${res.status})`)
    );
  }
  return res.json();
}

export async function getUser(
  token: string,
  userId: number
): Promise<UserRead> {
  const res = await fetch(`${API_BASE}${USERS_PATH}/${userId}`, {
    headers: authHeaders(token),
  });
  if (!res.ok) {
    throw new Error(
      await extractError(res, `Failed to fetch user (${res.status})`)
    );
  }
  return res.json();
}

export async function createUser(
  token: string,
  payload: UserCreate
): Promise<UserRead> {
  const res = await fetch(`${API_BASE}${USERS_PATH}/`, {
    method: "POST",
    headers: authHeaders(token, true),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await extractError(res, "Failed to create user"));
  }
  return res.json();
}

export async function updateUser(
  token: string,
  userId: number,
  payload: UserUpdate
): Promise<UserRead> {
  const res = await fetch(`${API_BASE}${USERS_PATH}/${userId}`, {
    method: "PUT",
    headers: authHeaders(token, true),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await extractError(res, "Failed to update user"));
  }
  return res.json();
}

export async function deleteUser(token: string, userId: number): Promise<void> {
  const res = await fetch(`${API_BASE}${USERS_PATH}/${userId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  if (!res.ok) {
    // success is 204 No Content
    throw new Error(await extractError(res, "Failed to delete user"));
  }
}

// POST /users/{id}/approve - assigns effective role + approves. 400 if already approved.
export async function approveUser(
  token: string,
  userId: number,
  role: Role
): Promise<UserRead> {
  const res = await fetch(`${API_BASE}${USERS_PATH}/${userId}/approve`, {
    method: "POST",
    headers: authHeaders(token, true),
    body: JSON.stringify({ role }),
  });
  if (!res.ok) {
    throw new Error(await extractError(res, "Failed to approve user"));
  }
  return res.json();
}

// POST /users/{id}/reject - deletes the pending registration. 204. 400 if already approved.
export async function rejectUser(token: string, userId: number): Promise<void> {
  const res = await fetch(`${API_BASE}${USERS_PATH}/${userId}/reject`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) {
    throw new Error(await extractError(res, "Failed to reject user"));
  }
}
