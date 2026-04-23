import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useCalculator } from "@/hooks/useCalculator";

const stableGetAccessToken = vi.fn(() => "fake-token");

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: stableGetAccessToken,
  }),
}));

describe("useCalculator Hook", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    global.fetch = vi.fn();
  });

  it("sends POST request and returns planting plan data sucessfully", async () => {
    const mockData = {
      id: 1,
      pre_slope_count: 100,
      aligned_count: 80,
      optimal_angle: 20,
    };

    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { result } = renderHook(() => useCalculator("123"));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/sapling_estimation/calculate"),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          Authorization: "Bearer fake-token",
        }),
      })
    );

    expect(result.current.result?.aligned_count).toBe(80);
    expect(result.current.hasSearched).toBe(true);
  });

  it("does not fetch data when farmId is empty", async () => {
    const { result } = renderHook(() => useCalculator(""));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.hasSearched).toBe(false);
  });

  it("handles API errors by returning an error message", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      json: async () => ({ message: "Internal Server Error" }),
    });

    const { result } = renderHook(() => useCalculator("123"));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe("Internal Server Error");
    expect(result.current.hasSearched).toBe(false);
  });
});
