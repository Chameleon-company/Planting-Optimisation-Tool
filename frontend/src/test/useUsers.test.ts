// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";

import { useUsers } from "@/hooks/useUsers";
import {
  listUsers,
  listPending,
  createUser as apiCreateUser,
  updateUser as apiUpdateUser,
  deleteUser as apiDeleteUser,
  approveUser as apiApproveUser,
  rejectUser as apiRejectUser,
} from "@/utils/usersAPI";
import type { UserRead } from "@/utils/usersAPI";

const { getAccessToken, authState } = vi.hoisted(() => ({
  getAccessToken: vi.fn<() => string | null>(() => "fake-token"),
  authState: {
    user: { id: 99, role: "admin" } as { id: number; role: string } | null,
  },
}));

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({ getAccessToken, user: authState.user }),
}));

vi.mock("@/utils/usersAPI", () => ({
  listUsers: vi.fn(),
  listPending: vi.fn(),
  createUser: vi.fn(),
  updateUser: vi.fn(),
  deleteUser: vi.fn(),
  approveUser: vi.fn(),
  rejectUser: vi.fn(),
}));

const makeUser = (id: number, role: UserRead["role"]): UserRead => ({
  id,
  role,
  name: `User ${id}`,
  email: `user${id}@example.com`,
  is_approved: true,
  requested_role: null,
});

describe("useUsers", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockReturnValue("fake-token");
    authState.user = { id: 99, role: "admin" };
    vi.mocked(listUsers).mockResolvedValue([]);
    vi.mocked(listPending).mockResolvedValue([]);
  });

  it("loads both lists on mount for an admin", async () => {
    vi.mocked(listUsers).mockResolvedValue([makeUser(1, "officer")]);
    vi.mocked(listPending).mockResolvedValue([makeUser(2, "officer")]);

    const { result } = renderHook(() => useUsers());

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(listUsers).toHaveBeenCalledTimes(1);
    expect(listPending).toHaveBeenCalledTimes(1);
    expect(result.current.allUsers).toHaveLength(1);
    expect(result.current.pendingUsers).toHaveLength(1);
  });

  it("sorts the full list by role admin/supervisor/officer then id", async () => {
    vi.mocked(listUsers).mockResolvedValue([
      makeUser(5, "officer"),
      makeUser(2, "admin"),
      makeUser(8, "supervisor"),
      makeUser(1, "officer"),
      makeUser(3, "admin"),
    ]);

    const { result } = renderHook(() => useUsers());

    await waitFor(() => expect(result.current.allUsers).toHaveLength(5));

    expect(result.current.allUsers.map(u => u.id)).toEqual([2, 3, 8, 1, 5]);
  });

  it("sorts the pending queue by id", async () => {
    vi.mocked(listPending).mockResolvedValue([
      makeUser(8, "officer"),
      makeUser(2, "officer"),
      makeUser(5, "officer"),
    ]);

    const { result } = renderHook(() => useUsers());

    await waitFor(() => expect(result.current.pendingUsers).toHaveLength(3));

    expect(result.current.pendingUsers.map(u => u.id)).toEqual([2, 5, 8]);
  });

  it("does not fetch the pending queue for a non-admin", async () => {
    authState.user = { id: 7, role: "supervisor" };
    vi.mocked(listUsers).mockResolvedValue([makeUser(1, "officer")]);

    const { result } = renderHook(() => useUsers());

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(listUsers).toHaveBeenCalledTimes(1);
    expect(listPending).not.toHaveBeenCalled();
    expect(result.current.pendingUsers).toEqual([]);
  });

  it("clears the lists and skips fetching when there is no token", async () => {
    getAccessToken.mockReturnValue(null);

    const { result } = renderHook(() => useUsers());

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(listUsers).not.toHaveBeenCalled();
    expect(result.current.allUsers).toEqual([]);
    expect(result.current.error).toBeNull();
  });

  it("surfaces a fetch error and empties the list", async () => {
    vi.mocked(listUsers).mockRejectedValue(new Error("Boom"));

    const { result } = renderHook(() => useUsers());

    await waitFor(() => expect(result.current.error).toBe("Boom"));
    expect(result.current.allUsers).toEqual([]);
  });

  describe("client-side pagination", () => {
    it("slices the list into pages and reports the page count", async () => {
      const many = Array.from({ length: 65 }, (_, i) =>
        makeUser(i + 1, "officer")
      );
      vi.mocked(listUsers).mockResolvedValue(many);

      const { result } = renderHook(() => useUsers());

      await waitFor(() => expect(result.current.totalUsers).toBe(65));

      expect(result.current.users).toHaveLength(30);
      expect(result.current.users[0].id).toBe(1);
      expect(result.current.totalPages).toBe(3);

      act(() => result.current.setPage(1));
      expect(result.current.users[0].id).toBe(31);
      expect(result.current.users).toHaveLength(30);

      act(() => result.current.setPage(2));
      expect(result.current.users).toHaveLength(5);
    });
  });

  describe("mutations", () => {
    it("createUser calls the API then refetches the main list", async () => {
      const { result } = renderHook(() => useUsers());
      await waitFor(() => expect(listUsers).toHaveBeenCalledTimes(1));

      vi.mocked(apiCreateUser).mockResolvedValue(makeUser(10, "officer"));

      await act(async () => {
        await result.current.createUser({
          email: "x@example.com",
          name: "X",
          password: "pw",
        });
      });

      expect(apiCreateUser).toHaveBeenCalledWith("fake-token", {
        email: "x@example.com",
        name: "X",
        password: "pw",
      });
      expect(listUsers).toHaveBeenCalledTimes(2);
    });

    it("updateUser passes the id and payload through", async () => {
      const { result } = renderHook(() => useUsers());
      await waitFor(() => expect(listUsers).toHaveBeenCalledTimes(1));

      vi.mocked(apiUpdateUser).mockResolvedValue(makeUser(3, "supervisor"));

      await act(async () => {
        await result.current.updateUser(3, { role: "supervisor" });
      });

      expect(apiUpdateUser).toHaveBeenCalledWith("fake-token", 3, {
        role: "supervisor",
      });
    });

    it("deleteUser calls the API then refetches", async () => {
      const { result } = renderHook(() => useUsers());
      await waitFor(() => expect(listUsers).toHaveBeenCalledTimes(1));

      vi.mocked(apiDeleteUser).mockResolvedValue(undefined);

      await act(async () => {
        await result.current.deleteUser(4);
      });

      expect(apiDeleteUser).toHaveBeenCalledWith("fake-token", 4);
      expect(listUsers).toHaveBeenCalledTimes(2);
    });

    it("approveUser refetches BOTH lists", async () => {
      const { result } = renderHook(() => useUsers());
      await waitFor(() => {
        expect(listUsers).toHaveBeenCalledTimes(1);
        expect(listPending).toHaveBeenCalledTimes(1);
      });

      vi.mocked(apiApproveUser).mockResolvedValue(makeUser(2, "supervisor"));

      await act(async () => {
        await result.current.approveUser(2, "supervisor");
      });

      expect(apiApproveUser).toHaveBeenCalledWith(
        "fake-token",
        2,
        "supervisor"
      );
      expect(listUsers).toHaveBeenCalledTimes(2);
      expect(listPending).toHaveBeenCalledTimes(2);
    });

    it("rejectUser refetches BOTH lists", async () => {
      const { result } = renderHook(() => useUsers());
      await waitFor(() => {
        expect(listUsers).toHaveBeenCalledTimes(1);
        expect(listPending).toHaveBeenCalledTimes(1);
      });

      vi.mocked(apiRejectUser).mockResolvedValue(undefined);

      await act(async () => {
        await result.current.rejectUser(2);
      });

      expect(apiRejectUser).toHaveBeenCalledWith("fake-token", 2);
      expect(listUsers).toHaveBeenCalledTimes(2);
      expect(listPending).toHaveBeenCalledTimes(2);
    });

    it("sets the error and re-throws when a mutation fails", async () => {
      const { result } = renderHook(() => useUsers());
      await waitFor(() => expect(listUsers).toHaveBeenCalledTimes(1));

      vi.mocked(apiDeleteUser).mockRejectedValue(new Error("nope"));

      await act(async () => {
        await expect(result.current.deleteUser(4)).rejects.toThrow("nope");
      });

      await waitFor(() => expect(result.current.error).toBe("nope"));
    });

    it("throws 'Not authenticated' when the token is gone at mutation time", async () => {
      const { result } = renderHook(() => useUsers());
      await waitFor(() => expect(listUsers).toHaveBeenCalledTimes(1));

      getAccessToken.mockReturnValue(null);

      await act(async () => {
        await expect(result.current.deleteUser(4)).rejects.toThrow(
          "Not authenticated"
        );
      });

      expect(apiDeleteUser).not.toHaveBeenCalled();
    });
  });
});
