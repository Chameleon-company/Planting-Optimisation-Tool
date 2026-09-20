// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useCalculator, DEFAULT_CALC_PARAMS } from "@/hooks/useCalculator";

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      id: 1,
      name: "Test User",
      email: "test@test.com",
      role: "admin",
      farms: [],
    },
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}));

const mockResult = {
  id: 1,
  pre_slope_count: 100,
  aligned_count: 80,
  optimal_angle: 20,
};

describe("useCalculator Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it("sends POST request with correct params and returns result", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResult,
    });

    const { result } = renderHook(() =>
      useCalculator("123", DEFAULT_CALC_PARAMS)
    );

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/sapling_estimation/calculate"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          farm_id: 123,
          spacing_x: DEFAULT_CALC_PARAMS.spacingX,
          spacing_y: DEFAULT_CALC_PARAMS.spacingY,
          max_slope: DEFAULT_CALC_PARAMS.maxSlope,
        }),
      })
    );

    expect(result.current.result).toEqual(mockResult);
    expect(result.current.hasSearched).toBe(true);
    expect(result.current.error).toBe(null);
  });

  it("does not fetch when farmId is empty", () => {
    const { result } = renderHook(() => useCalculator("", DEFAULT_CALC_PARAMS));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.hasSearched).toBe(false);
  });

  it("sets error from API error message on non-ok response", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      json: async () => ({ detail: "Farm not found" }),
    });

    const { result } = renderHook(() =>
      useCalculator("123", DEFAULT_CALC_PARAMS)
    );

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe("Farm not found");
    expect(result.current.hasSearched).toBe(false);
    expect(result.current.result).toBe(null);
  });

  it("sets a fallback error on network failure", async () => {
    (global.fetch as Mock).mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() =>
      useCalculator("123", DEFAULT_CALC_PARAMS)
    );

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe("Network error");
    expect(result.current.hasSearched).toBe(false);
  });
});
