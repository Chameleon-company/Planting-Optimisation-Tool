import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { AuthProvider, useAuth } from "../contexts/AuthContext";

const mockFetch = vi.fn();

Object.defineProperty(globalThis, "fetch", {
  value: mockFetch,
  writable: true,
});

const TestComponent = () => {
  const { user, login, logout, isLoading } = useAuth();

  return (
    <div>
      <p>{user ? `Logged in as ${user.name}` : "Not logged in"}</p>
      <p>{isLoading ? "Loading" : "Idle"}</p>
      <button
        onClick={() =>
          login({ email: "admin@test.com", password: "Password123!" })
        }
      >
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe("AuthContext", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it("should start logged out when there is no token", () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText("Not logged in")).toBeInTheDocument();
    expect(screen.getByText("Idle")).toBeInTheDocument();
  });

  it("should log in and set the real user from backend responses", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: "test-token",
          token_type: "bearer",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 1,
          name: "Admin User",
          email: "admin@test.com",
          role: "admin",
        }),
      });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await userEvent.click(screen.getByText("Login"));

    await waitFor(() => {
      expect(screen.getByText("Logged in as Admin User")).toBeInTheDocument();
    });

    expect(localStorage.getItem("access_token")).toBe("test-token");
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });

  it("should clear user and token after logout", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: "test-token",
          token_type: "bearer",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 1,
          name: "Admin User",
          email: "admin@test.com",
          role: "admin",
        }),
      });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await userEvent.click(screen.getByText("Login"));

    await waitFor(() => {
      expect(screen.getByText("Logged in as Admin User")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText("Logout"));

    expect(screen.getByText("Not logged in")).toBeInTheDocument();
    expect(localStorage.getItem("access_token")).toBeNull();
  });

  it("should restore user from localStorage token on mount", async () => {
    localStorage.setItem("access_token", "stored-token");

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 2,
        name: "Stored Admin",
        email: "stored@test.com",
        role: "admin",
      }),
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Logged in as Stored Admin")).toBeInTheDocument();
    });

    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it("should throw if useAuth is used outside provider", () => {
    expect(() => render(<TestComponent />)).toThrow(
      "useAuth must be used inside <AuthProvider>"
    );
  });
});
