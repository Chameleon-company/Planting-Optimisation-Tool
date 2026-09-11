// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useCalculator, DEFAULT_CALC_PARAMS } from "@/hooks/useCalculator";

const stableGetAccessToken = vi.fn<() => string | null>(() => "fake-token");

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: stableGetAccessToken,
  }),
}));

const ONE_FARM = [123];
const THREE_FARMS = [1, 2, 3];
const NO_FARMS: number[] = [];

const mockResponse = {
  status: "ok",
  farm_count: 1,
  results: [
    {
      farm_id: 123,
      status: "success",
      pre_slope_count: 100,
      aligned_count: 80,
      optimal_angle: 20,
    },
  ],
};

describe("useCalculator Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it("sends POST request with correct params and returns results", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() =>
      useCalculator(ONE_FARM, DEFAULT_CALC_PARAMS)
    );

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/sapling_estimation/calculate"),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          Authorization: "Bearer fake-token",
        }),
        body: JSON.stringify({
          farm_ids: [123],
          spacing_x: DEFAULT_CALC_PARAMS.spacingX,
          spacing_y: DEFAULT_CALC_PARAMS.spacingY,
          max_slope: DEFAULT_CALC_PARAMS.maxSlope,
        }),
      })
    );

    expect(result.current.results).toEqual(mockResponse.results);
    expect(result.current.hasSearched).toBe(true);
    expect(result.current.error).toBe(null);
  });

  it("sends every requested id in the farm_ids array", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "ok",
        farm_count: 3,
        results: [
          { farm_id: 1, status: "success" },
          { farm_id: 2, status: "success" },
          { farm_id: 3, status: "failed", message: "No boundary data" },
        ],
      }),
    });

    const { result } = renderHook(() =>
      useCalculator(THREE_FARMS, DEFAULT_CALC_PARAMS)
    );

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    const body = JSON.parse(
      (global.fetch as Mock).mock.calls[0][1].body as string
    );
    expect(body.farm_ids).toEqual([1, 2, 3]);
    expect(result.current.results).toHaveLength(3);
  });

  it("does not fetch when farmIds is empty", () => {
    const { result } = renderHook(() =>
      useCalculator(NO_FARMS, DEFAULT_CALC_PARAMS)
    );

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.hasSearched).toBe(false);
    expect(result.current.results).toEqual([]);
  });

  it("sets error from API error message on non-ok response", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      json: async () => ({ detail: "Farm not found" }),
    });

    const { result } = renderHook(() =>
      useCalculator(ONE_FARM, DEFAULT_CALC_PARAMS)
    );

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe("Farm not found");
    expect(result.current.hasSearched).toBe(false);
    expect(result.current.results).toEqual([]);
  });

  it("sets a fallback error on network failure", async () => {
    (global.fetch as Mock).mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() =>
      useCalculator(ONE_FARM, DEFAULT_CALC_PARAMS)
    );

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe("Network error");
    expect(result.current.hasSearched).toBe(false);
  });

  it("sets login error and does not fetch when token is missing", async () => {
    stableGetAccessToken.mockReturnValueOnce(null);

    const { result } = renderHook(() =>
      useCalculator(ONE_FARM, DEFAULT_CALC_PARAMS)
    );

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.error).toBe("Please log in to continue.");
  });
});
