import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import App from "../App";

vi.mock("@/components/calculator/FarmMap", () => ({
  default: () => null,
}));

vi.mock("../contexts/AuthContext", async () => {
  const actual = await vi.importActual<
    typeof import("../contexts/AuthContext")
  >("../contexts/AuthContext");

  return {
    ...actual,
    useAuth: () => ({
      user: { role: "admin" },
      getAccessToken: () => "test-token",
      logout: vi.fn(),
    }),
  };
});

describe("App", () => {
  it("registers the admin species route", async () => {
    window.history.pushState({}, "", "/admin/species");

    render(<App />);

    expect(
      await screen.findByRole("button", { name: /add species/i })
    ).toBeInTheDocument();
  });

  it("renders forgot password page route", () => {
    window.history.pushState({}, "", "/forgot-password");

    render(<App />);

    expect(
      screen.getByRole("heading", { name: /forgot your password/i })
    ).toBeInTheDocument();
  });

  it("renders reset password page route", () => {
    window.history.pushState({}, "", "/reset-password?token=reset-token");

    render(<App />);

    expect(
      screen.getByRole("heading", { name: /reset your password/i })
    ).toBeInTheDocument();
  });
});
