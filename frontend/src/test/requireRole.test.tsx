import "@testing-library/jest-dom/vitest";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import RequireRole from "../components/auth/RequireRole";

const mockUseAuth = vi.fn();

vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("RequireRole", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading state while auth is restoring", () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: true,
    });

    render(
      <MemoryRouter>
        <RequireRole allowedRoles={["admin"]}>
          <div>Secret Admin Content</div>
        </RequireRole>
      </MemoryRouter>
    );

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("redirects logged out users away from protected route", () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
    });

    render(
      <MemoryRouter initialEntries={["/admin"]}>
        <RequireRole allowedRoles={["admin"]}>
          <div>Secret Admin Content</div>
        </RequireRole>
      </MemoryRouter>
    );

    expect(screen.queryByText("Secret Admin Content")).not.toBeInTheDocument();
  });

  it("redirects users with wrong role", () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 3,
        name: "Officer User",
        email: "officer@test.com",
        role: "officer",
        farms: [],
      },
      isLoading: false,
    });

    render(
      <MemoryRouter initialEntries={["/admin"]}>
        <RequireRole allowedRoles={["admin"]}>
          <div>Secret Admin Content</div>
        </RequireRole>
      </MemoryRouter>
    );

    expect(screen.queryByText("Secret Admin Content")).not.toBeInTheDocument();
  });

  it("renders children for allowed admin user", () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        name: "Admin User",
        email: "admin@test.com",
        role: "admin",
        farms: [],
      },
      isLoading: false,
    });

    render(
      <MemoryRouter>
        <RequireRole allowedRoles={["admin"]}>
          <div>Secret Admin Content</div>
        </RequireRole>
      </MemoryRouter>
    );

    expect(screen.getByText("Secret Admin Content")).toBeInTheDocument();
  });
});
