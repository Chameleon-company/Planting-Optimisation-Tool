import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useResetPassword } from "../hooks/useResetPassword";

const mockFetch = vi.fn();

describe("useResetPassword", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal("fetch", mockFetch);
  });

  it("sends reset password request with token and new password", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: vi.fn(),
    });

    const { result } = renderHook(() => useResetPassword());

    let didReset = false;

    await act(async () => {
      didReset = await result.current.resetPassword(
        "reset-token",
        "Password1234@"
      );
    });
    expect(didReset).toBe(true);

    expect(mockFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8080/auth/reset-password",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: "reset-token",
          new_password: "Password1234@",
        }),
      }
    );

    expect(result.current.errorMessage).toBe("");
    expect(result.current.successMessage).toBe(
      "Password reset successfully. You can now sign in."
    );
    expect(result.current.isLoading).toBe(false);
  });

  it("shows backend error detail when reset token is invalid or expired", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: vi.fn().mockResolvedValueOnce({
        detail: "Invalid or expired token",
      }),
    });

    const { result } = renderHook(() => useResetPassword());

    let didReset = true;

    await act(async () => {
      didReset = await result.current.resetPassword(
        "expired-token",
        "Password1234@"
      );
    });
    expect(didReset).toBe(false);

    expect(result.current.successMessage).toBe("");
    expect(result.current.errorMessage).toBe("Invalid or expired token");
    expect(result.current.isLoading).toBe(false);
  });

  it("shows backend password validation message when password is invalid", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: vi.fn().mockResolvedValueOnce({
        detail: "Password must contain at least one number",
      }),
    });

    const { result } = renderHook(() => useResetPassword());

    await act(async () => {
      await result.current.resetPassword("reset-token", "PasswordOnly!");
    });

    expect(result.current.successMessage).toBe("");
    expect(result.current.errorMessage).toBe(
      "Password must contain at least one number"
    );
    expect(result.current.isLoading).toBe(false);
  });

  it("shows default error when backend error response has no readable JSON", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: vi.fn().mockRejectedValueOnce(new Error("Invalid JSON")),
    });

    const { result } = renderHook(() => useResetPassword());

    await act(async () => {
      await result.current.resetPassword("reset-token", "Password1234@");
    });

    expect(result.current.successMessage).toBe("");
    expect(result.current.errorMessage).toBe(
      "Unable to reset password. Please try again."
    );
    expect(result.current.isLoading).toBe(false);
  });

  it("shows network error message when fetch rejects with an Error", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network unavailable"));

    const { result } = renderHook(() => useResetPassword());

    await act(async () => {
      await result.current.resetPassword("reset-token", "Password1234@");
    });

    expect(result.current.successMessage).toBe("");
    expect(result.current.errorMessage).toBe("Network unavailable");
    expect(result.current.isLoading).toBe(false);
  });

  it("shows fallback error when fetch rejects with a non-error value", async () => {
    mockFetch.mockRejectedValueOnce("unknown failure");

    const { result } = renderHook(() => useResetPassword());

    await act(async () => {
      await result.current.resetPassword("reset-token", "Password1234@");
    });

    await waitFor(() => {
      expect(result.current.errorMessage).toBe(
        "Unable to reset password. Please try again."
      );
    });

    expect(result.current.successMessage).toBe("");
    expect(result.current.isLoading).toBe(false);
  });
});
