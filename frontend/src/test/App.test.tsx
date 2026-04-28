import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import App from "../App";

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
});
