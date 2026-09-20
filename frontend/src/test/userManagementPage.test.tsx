import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { HelmetProvider } from "react-helmet-async";

import AdminUsersPage from "@/pages/admin/AdminUsers";
import type { UserRead } from "@/utils/usersAPI";

vi.mock("@/hooks/useUsers", () => ({ useUsers: vi.fn() }));
vi.mock("@/contexts/AuthContext", () => ({ useAuth: vi.fn() }));
vi.mock("react-hot-toast", () => ({ default: { error: vi.fn() } }));

import { useUsers } from "@/hooks/useUsers";
import { useAuth } from "@/contexts/AuthContext";

const makeUser = (
  id: number,
  role: UserRead["role"],
  overrides: Partial<UserRead> = {}
): UserRead => ({
  id,
  role,
  name: `User ${id}`,
  email: `user${id}@example.com`,
  is_approved: true,
  requested_role: null,
  ...overrides,
});

const baseHook = {
  users: [] as UserRead[],
  pendingUsers: [] as UserRead[],
  isLoading: false,
  isMutating: false,
  error: null as string | null,
  page: 0,
  setPage: vi.fn(),
  totalPages: 1,
  totalUsers: 0,
  updateUser: vi.fn(),
  deleteUser: vi.fn().mockResolvedValue(undefined),
  approveUser: vi.fn().mockResolvedValue(undefined),
  rejectUser: vi.fn().mockResolvedValue(undefined),
};

const mockHook = (overrides: Partial<typeof baseHook> = {}) =>
  vi.mocked(useUsers).mockReturnValue({
    ...baseHook,
    ...overrides,
  } as unknown as ReturnType<typeof useUsers>);

const mockAuth = (user: { id: number; role: string } | null) =>
  vi.mocked(useAuth).mockReturnValue({
    user,
  } as unknown as ReturnType<typeof useAuth>);

const renderPage = () =>
  render(
    <HelmetProvider>
      <AdminUsersPage />
    </HelmetProvider>
  );

describe("AdminUsersPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAuth({ id: 99, role: "admin" });
    mockHook();
  });

  it("shows an access-denied message for non-admins", () => {
    mockAuth({ id: 5, role: "officer" });

    renderPage();

    expect(screen.getByText(/access denied/i)).toBeInTheDocument();
    expect(screen.queryByText(/all users/i)).not.toBeInTheDocument();
  });

  it("shows a loading state while the list is loading", () => {
    mockHook({ isLoading: true });

    renderPage();

    expect(screen.getByText(/loading users/i)).toBeInTheDocument();
    expect(screen.queryByText(/no users to display/i)).not.toBeInTheDocument();
  });

  it("renders the All Users section with the user count and table rows", () => {
    mockHook({ users: [makeUser(1, "admin", { name: "Ada" })], totalUsers: 3 });
    renderPage();

    expect(
      screen.getByRole("heading", { name: /all users/i })
    ).toBeInTheDocument();
    expect(screen.getByText(/3 users/i)).toBeInTheDocument();
    expect(screen.getByText("Ada")).toBeInTheDocument();
  });

  it("flags the number of accounts awaiting approval", () => {
    mockHook({
      totalUsers: 3,
      pendingUsers: [makeUser(2, "officer"), makeUser(3, "officer")],
    });
    renderPage();

    expect(screen.getByText(/2 awaiting approval/i)).toBeInTheDocument();
  });

  it("shows the empty pending fallback when the queue is empty", () => {
    mockHook({ pendingUsers: [] });

    renderPage();

    expect(
      screen.getByText(/no accounts are waiting for approval/i)
    ).toBeInTheDocument();
  });

  it("renders pagination controls when there is more than one page", () => {
    mockHook({ totalPages: 2, totalUsers: 45 });

    const { container } = renderPage();

    expect(container.querySelector(".users-page-indicator")?.textContent).toBe(
      "Page 1 of 2"
    );
    expect(screen.getByRole("button", { name: /next/i })).toBeInTheDocument();
  });
});
