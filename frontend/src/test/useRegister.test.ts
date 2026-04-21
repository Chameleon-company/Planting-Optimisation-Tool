// useRegister.test.ts
//
// Tests for the useRegister hook in isolation.
//
// Strategy: mock the global fetch so we control what the API returns,
// then assert that the hook updates its state correctly.
// The component that calls this hook is tested separately in registerPage.test.tsx.

import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, renderHook } from "@testing-library/react";

import { useRegister } from "../hooks/useRegister";

// Sample registration payload used across multiple tests
const validPayload = {
  name: "Test User",
  email: "test@example.com",
  password: "Password123!",
  role: "officer",
};

describe("useRegister", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("starts in an idle state with no messages", () => {
    const { result } = renderHook(() => useRegister());

    expect(result.current.isLoading).toBe(false);
    expect(result.current.successMessage).toBe("");
    expect(result.current.errorMessage).toBe("");
  });

  it("sets successMessage when registration succeeds", async () => {
    // Simulate a 200 OK response from the backend
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    } as Response);

    const { result } = renderHook(() => useRegister());

    // act() ensures all state updates triggered by register() are flushed
    await act(async () => {
      await result.current.register(validPayload);
    });

    expect(result.current.successMessage).toMatch(/registration successful/i);
    expect(result.current.successMessage).toMatch(/check your email/i);
    expect(result.current.errorMessage).toBe("");
    expect(result.current.isLoading).toBe(false);
  });

  it("sets errorMessage with backend detail when email is already registered", async () => {
    // Simulate the backend returning 400 with a detail field
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "Email already registered." }),
    } as Response);

    const { result } = renderHook(() => useRegister());

    await act(async () => {
      await result.current.register(validPayload);
    });

    expect(result.current.errorMessage).toBe("Email already registered.");
    expect(result.current.successMessage).toBe("");
    expect(result.current.isLoading).toBe(false);
  });

  it("sets errorMessage with backend detail when password does not meet requirements", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      json: async () => ({
        detail: "Password does not meet strength requirements.",
      }),
    } as Response);

    const { result } = renderHook(() => useRegister());

    await act(async () => {
      await result.current.register({ ...validPayload, password: "weak" });
    });

    expect(result.current.errorMessage).toBe(
      "Password does not meet strength requirements."
    );
    expect(result.current.successMessage).toBe("");
  });

  it("sets a fallback errorMessage when the backend returns no detail field", async () => {
    // Some error responses may not include a detail field
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      json: async () => ({}),
    } as Response);

    const { result } = renderHook(() => useRegister());

    await act(async () => {
      await result.current.register(validPayload);
    });

    expect(result.current.errorMessage).toBe(
      "Registration failed. Please try again."
    );
  });

  it("sets a fallback errorMessage when fetch throws a network error", async () => {
    // Simulate a network failure (no internet, server unreachable, etc.)
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useRegister());

    await act(async () => {
      await result.current.register(validPayload);
    });

    expect(result.current.errorMessage).toBe("Network error");
    expect(result.current.successMessage).toBe("");
    expect(result.current.isLoading).toBe(false);
  });
});
