import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useForgotPassword } from "../hooks/useForgotPassword";

const mockFetch = vi.fn();

describe("useForgotPassword", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal("fetch", mockFetch);
  });

  it("sends forgot password request with the entered email", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: vi.fn(),
    });

    const { result } = renderHook(() => useForgotPassword());

    await act(async () => {
      await result.current.forgotPassword("user@example.com");
    });

    expect(mockFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8080/auth/forgot-password",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "user@example.com" }),
      }
    );

    expect(result.current.errorMessage).toBe("");
    expect(result.current.successMessage).toBe(
      "Please check your inbox for a password reset link. If this email is registered, the link will arrive shortly."
    );
    expect(result.current.isLoading).toBe(false);
  });

  it("shows backend error detail when forgot password request fails", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: vi.fn().mockResolvedValueOnce({
        detail: "Too many requests. Please try again later.",
      }),
    });

    const { result } = renderHook(() => useForgotPassword());

    await act(async () => {
      await result.current.forgotPassword("user@example.com");
    });

    expect(result.current.successMessage).toBe("");
    expect(result.current.errorMessage).toBe(
      "Too many requests. Please try again later."
    );
    expect(result.current.isLoading).toBe(false);
  });

  it("shows default error when backend error response has no readable JSON", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: vi.fn().mockRejectedValueOnce(new Error("Invalid JSON")),
    });

    const { result } = renderHook(() => useForgotPassword());

    await act(async () => {
      await result.current.forgotPassword("user@example.com");
    });

    expect(result.current.successMessage).toBe("");
    expect(result.current.errorMessage).toBe(
      "Unable to send reset link. Please try again."
    );
    expect(result.current.isLoading).toBe(false);
  });

  it("shows network error message when fetch rejects with an Error", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network unavailable"));

    const { result } = renderHook(() => useForgotPassword());

    await act(async () => {
      await result.current.forgotPassword("user@example.com");
    });

    expect(result.current.successMessage).toBe("");
    expect(result.current.errorMessage).toBe("Network unavailable");
    expect(result.current.isLoading).toBe(false);
  });

  it("shows fallback error when fetch rejects with a non-error value", async () => {
    mockFetch.mockRejectedValueOnce("unknown failure");

    const { result } = renderHook(() => useForgotPassword());

    await act(async () => {
      await result.current.forgotPassword("user@example.com");
    });

    await waitFor(() => {
      expect(result.current.errorMessage).toBe(
        "Unable to send reset link. Please try again."
      );
    });

    expect(result.current.successMessage).toBe("");
    expect(result.current.isLoading).toBe(false);
  });
});
