// useVerifyEmail.test.ts
//
// Tests for the useVerifyEmail hook in isolation.
//
// Strategy: mock the global fetch so we control what the API returns,
// then assert that the hook updates its status correctly.
// The component that calls this hook is tested separately in verifyEmailPage.test.tsx.

import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, renderHook } from "@testing-library/react";

import { useVerifyEmail } from "../hooks/useVerifyEmail";

describe("useVerifyEmail", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("starts in loading state with no error message", () => {
    const { result } = renderHook(() => useVerifyEmail());

    expect(result.current.status).toBe("loading");
    expect(result.current.errorMessage).toBe("");
  });

  it("sets status to success when verification succeeds", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: "Email verified successfully" }),
    } as Response);

    const { result } = renderHook(() => useVerifyEmail());

    await act(async () => {
      await result.current.verify("valid-token");
    });

    expect(result.current.status).toBe("success");
    expect(result.current.errorMessage).toBe("");
  });

  it("sets status to error with backend detail when token is invalid or expired", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "Invalid or expired token" }),
    } as Response);

    const { result } = renderHook(() => useVerifyEmail());

    await act(async () => {
      await result.current.verify("expired-token");
    });

    expect(result.current.status).toBe("error");
    expect(result.current.errorMessage).toBe("Invalid or expired token");
  });

  it("sets a fallback errorMessage when the backend returns no detail field", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      json: async () => ({}),
    } as Response);

    const { result } = renderHook(() => useVerifyEmail());

    await act(async () => {
      await result.current.verify("token");
    });

    expect(result.current.status).toBe("error");
    expect(result.current.errorMessage).toBe(
      "Invalid or expired verification link."
    );
  });

  it("sets a fallback errorMessage when fetch throws a network error", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useVerifyEmail());

    await act(async () => {
      await result.current.verify("token");
    });

    expect(result.current.status).toBe("error");
    expect(result.current.errorMessage).toBe("Network error");
  });
});
