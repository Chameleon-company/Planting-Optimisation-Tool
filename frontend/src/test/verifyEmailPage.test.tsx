// verifyEmailPage.test.tsx
//
// Tests for the VerifyEmailPage UI component.
//
// Strategy: mock the useVerifyEmail hook and useSearchParams so this test
// file only cares about what the component renders for each status state.
// The hook's own behaviour (fetch calls, API errors) is tested separately
// in useVerifyEmail.test.ts.

import "@testing-library/jest-dom/vitest";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";

import VerifyEmailPage from "../pages/auth/VerifyEmailPage";

vi.mock("../hooks/useVerifyEmail", () => ({
  useVerifyEmail: vi.fn(),
}));

vi.mock("react-router-dom", async () => {
  const actual =
    await vi.importActual<typeof import("react-router-dom")>(
      "react-router-dom"
    );
  return {
    ...actual,
    useSearchParams: vi.fn(),
  };
});

import { useVerifyEmail } from "../hooks/useVerifyEmail";
import { useSearchParams } from "react-router-dom";

const mockVerify = vi.fn();

const defaultHookReturn = {
  status: "loading" as const,
  errorMessage: "",
  verify: mockVerify,
};

function renderPage() {
  return render(
    <HelmetProvider>
      <MemoryRouter>
        <VerifyEmailPage />
      </MemoryRouter>
    </HelmetProvider>
  );
}

describe("VerifyEmailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useVerifyEmail).mockReturnValue(defaultHookReturn);
    vi.mocked(useSearchParams).mockReturnValue([
      new URLSearchParams("token=abc123"),
      vi.fn(),
    ]);
  });

  it("shows loading state while verifying", () => {
    renderPage();

    expect(
      screen.getByRole("heading", { name: /verifying your email/i })
    ).toBeInTheDocument();
    expect(screen.getByText(/please wait/i)).toBeInTheDocument();
  });

  it("calls verify with the token on mount", () => {
    renderPage();

    expect(mockVerify).toHaveBeenCalledWith("abc123");
  });

  it("shows success state after verification", () => {
    vi.mocked(useVerifyEmail).mockReturnValue({
      ...defaultHookReturn,
      status: "success",
    });

    renderPage();

    expect(
      screen.getByRole("heading", { name: /email verified/i })
    ).toBeInTheDocument();
    expect(
      screen.getByText(/your account has been activated/i)
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /sign in/i })).toHaveAttribute(
      "href",
      "/login"
    );
  });

  it("shows error state when verification fails", () => {
    vi.mocked(useVerifyEmail).mockReturnValue({
      ...defaultHookReturn,
      status: "error",
      errorMessage: "Invalid or expired verification link.",
    });

    renderPage();

    expect(
      screen.getByRole("heading", { name: /verification failed/i })
    ).toBeInTheDocument();
    expect(
      screen.getByText("Invalid or expired verification link.")
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /back to sign in/i })
    ).toBeInTheDocument();
  });

  it("shows invalid link state and does not call verify when no token in URL", () => {
    vi.mocked(useSearchParams).mockReturnValue([
      new URLSearchParams(""),
      vi.fn(),
    ]);

    renderPage();

    expect(
      screen.getByRole("heading", { name: /invalid link/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /back to sign in/i })
    ).toBeInTheDocument();
    expect(mockVerify).not.toHaveBeenCalled();
  });
});
