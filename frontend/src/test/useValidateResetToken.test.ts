import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useValidateResetToken } from "../hooks/useValidateResetToken";

const mockFetch = vi.fn();

describe("useValidateResetToken", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal("fetch", mockFetch);
  });

  it("starts with checking state when token exists", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: vi.fn().mockResolvedValueOnce({}),
    });

    const { result } = renderHook(() => useValidateResetToken("valid-token"));

    expect(result.current.isCheckingToken).toBe(true);
    expect(result.current.tokenErrorMessage).toBe("");

    await waitFor(() => {
      expect(result.current.isCheckingToken).toBe(false);
    });
  });

  it("does not call backend when token is missing", async () => {
    const { result } = renderHook(() => useValidateResetToken(""));

    expect(mockFetch).not.toHaveBeenCalled();
    expect(result.current.isCheckingToken).toBe(false);
    expect(result.current.tokenErrorMessage).toBe(
      "This reset link is missing a token. Please request a new password reset email."
    );
  });

  it("validates token with backend when token exists", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: vi.fn().mockResolvedValueOnce({}),
    });

    const { result } = renderHook(() => useValidateResetToken("valid-token"));

    await waitFor(() => {
      expect(result.current.isCheckingToken).toBe(false);
    });

    expect(mockFetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8080/auth/reset-password/validate?token=valid-token",
      expect.objectContaining({
        method: "GET",
        signal: expect.any(AbortSignal),
      })
    );

    expect(result.current.tokenErrorMessage).toBe("");
  });

  it("shows backend error detail when token validation fails", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: vi.fn().mockResolvedValueOnce({
        detail: "Invalid or expired token",
      }),
    });

    const { result } = renderHook(() => useValidateResetToken("expired-token"));

    await waitFor(() => {
      expect(result.current.isCheckingToken).toBe(false);
    });

    expect(result.current.tokenErrorMessage).toBe("Invalid or expired token");
  });

  it("shows fallback message when backend validation fails without detail", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: vi.fn().mockResolvedValueOnce({}),
    });

    const { result } = renderHook(() => useValidateResetToken("bad-token"));

    await waitFor(() => {
      expect(result.current.isCheckingToken).toBe(false);
    });

    expect(result.current.tokenErrorMessage).toBe(
      "Invalid or expired reset link."
    );
  });

  it("shows fallback message when request fails", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useValidateResetToken("valid-token"));

    await waitFor(() => {
      expect(result.current.isCheckingToken).toBe(false);
    });

    expect(result.current.tokenErrorMessage).toBe(
      "Unable to validate reset link. Please request a new password reset email."
    );
  });
});
