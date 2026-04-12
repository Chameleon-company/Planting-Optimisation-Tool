// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useRecommendations } from "@/hooks/useRecommendations";

// Mock the external contexts and hooks
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({ getAccessToken: () => "fake-token" }),
}));

const mockThrowAsyncError = vi.fn();
vi.mock("@/hooks/useAsyncError", () => ({
  useAsyncError: () => mockThrowAsyncError,
}));

describe("useRecommendations Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it("fetches and returns recommendation data successfully", async () => {
    const mockData = {
      recommendations: [{ species_id: 1, score_mcda: 0.9 }],
      excluded_species: [{ id: 2, reasons: [] }],
    };

    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { result } = renderHook(() => useRecommendations("123"));

    // Wait until loading finishes
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/recommendations/123"),
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({
          Authorization: "Bearer fake-token",
          Accept: "application/json",
        }),
      })
    );

    // Validate returned data
    expect(result.current.recs.length).toBe(1);
    expect(result.current.excludes.length).toBe(1);
    expect(result.current.hasSearched).toBe(true);
  });

  it("does not fetch if farmId is empty", async () => {
    const { result } = renderHook(() => useRecommendations(""));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.hasSearched).toBe(false);
  });

  it("handles API errors using the async error boundary", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      text: async () => "Internal Server Error",
    });

    const { result } = renderHook(() => useRecommendations("123"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockThrowAsyncError).toHaveBeenCalledWith(
      new Error("Internal Server Error")
    );
    expect(result.current.recs.length).toBe(0);
  });
});
