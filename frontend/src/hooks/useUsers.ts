import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../contexts/AuthContext";
import {
  listUsers,
  listPending,
  createUser as apiCreateUser,
  updateUser as apiUpdateUser,
  deleteUser as apiDeleteUser,
  approveUser as apiApproveUser,
  rejectUser as apiRejectUser,
  type Role,
  type UserRead,
  type UserCreate,
  type UserUpdate,
} from "../utils/usersAPI";

const PAGE_SIZE = 30;

// Role display/sort order, Admin -> Supervisor -> Officer
const ROLE_ORDER: Record<Role, number> = {
  admin: 0,
  supervisor: 1,
  officer: 2,
};

export function useUsers() {
  const { getAccessToken, user } = useAuth();
  // Pending-approval actions are admin-only; used to gate that fetch
  const isAdmin = user?.role === "admin";

  const [allUsers, setAllUsers] = useState<UserRead[]>([]);
  const [pendingUsers, setPendingUsers] = useState<UserRead[]>([]);
  const [page, setPage] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isMutating, setIsMutating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch/GET the full user list (SUPERVISOR+), sorted by role
  const fetchUsers = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setAllUsers([]);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    // Try/catch, call the list API, sort the result by role then id
    try {
      const data = await listUsers(token);
      setAllUsers(
        [...data].sort((a, b) => {
          const byRole = ROLE_ORDER[a.role] - ROLE_ORDER[b.role];
          return byRole !== 0 ? byRole : a.id - b.id;
        })
      );
    } catch (err: unknown) {
      setAllUsers([]);
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
    } finally {
      setIsLoading(false);
    }
    // Refetch when getToken changes
  }, [getAccessToken]);

  const fetchPending = useCallback(async () => {
    const token = getAccessToken();
    if (!token || !isAdmin) {
      setPendingUsers([]);
      return;
    }

    // Try/catch, call the pending API, sort by id
    try {
      const data = await listPending(token);
      setPendingUsers([...data].sort((a, b) => a.id - b.id));
    } catch (err: unknown) {
      setPendingUsers([]);
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
    }
    // Re-run if the token or admin status changes
  }, [getAccessToken, isAdmin]);

  // On mount / user change, load both lists
  useEffect(() => {
    fetchUsers();
    fetchPending();
  }, [fetchUsers, fetchPending, user]);

  // Shared mutation runner, runs the passed-in call, refetches on success,
  // surfaces errors, and re-throws so callers can react too
  const runMutation = useCallback(
    async <T>(
      func: (token: string) => Promise<T>,
      options: { refetchPending?: boolean } = {}
    ): Promise<T> => {
      const token = getAccessToken();
      if (!token) throw new Error("Not authenticated");
      setIsMutating(true);
      setError(null);

      // Run the call, then refresh the list(s) it affected
      try {
        const result = await func(token);
        await fetchUsers();
        if (options.refetchPending) await fetchPending();
        return result;
      } catch (err: unknown) {
        setError(
          err instanceof Error ? err.message : "An unexpected error occurred"
        );
        throw err;
      } finally {
        setIsMutating(false);
      }
    },
    [getAccessToken, fetchUsers, fetchPending]
  );

  // Create/POST a new user, admins only
  const createUser = useCallback(
    (payload: UserCreate) =>
      runMutation(token => apiCreateUser(token, payload)),
    [runMutation]
  );

  // Update/PUT any field on a user, admins only
  const updateUser = useCallback(
    (userId: number, payload: UserUpdate) =>
      runMutation(token => apiUpdateUser(token, userId, payload)),
    [runMutation]
  );

  // Delete/DELETE a user, admins only, 204 No Content on success
  const deleteUser = useCallback(
    (userId: number) => runMutation(token => apiDeleteUser(token, userId)),
    [runMutation]
  );

  // Approve/POST a pending user with an role, admins only
  // Moves them from pending to approved, so refresh both lists
  const approveUser = useCallback(
    (userId: number, role: Role) =>
      runMutation(token => apiApproveUser(token, userId, role), {
        refetchPending: true,
      }),
    [runMutation]
  );

  // Reject/POST removes a pending registration, admins only, 204 on success
  // Drops them from pending, so refresh both lists
  const rejectUser = useCallback(
    (userId: number) =>
      runMutation(token => apiRejectUser(token, userId), {
        refetchPending: true,
      }),
    [runMutation]
  );

  const users = allUsers.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(allUsers.length / PAGE_SIZE);

  return {
    users,
    allUsers,
    pendingUsers,
    isLoading,
    isMutating,
    error,
    page,
    setPage,
    totalPages,
    totalUsers: allUsers.length,
    refetch: fetchUsers,
    refetchPending: fetchPending,
    createUser,
    updateUser,
    deleteUser,
    approveUser,
    rejectUser,
  };
}
