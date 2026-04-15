// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import {
  useAhpSpecies,
  useAhpFactors,
  useAhpCalculation,
} from "@/hooks/useAhp";

const stableGetAccessToken = vi.fn(() => "fake-token");

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: stableGetAccessToken,
  }),
}));

describe("AHP Hooks", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  describe("useAhpSpecies", () => {
    it("fetches and returns species dropdown data", async () => {
      const mockData = [
        { id: 1, name: "scientific", common_name: "Common Tree" },
      ];

      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => mockData,
      });

      const { result } = renderHook(() => useAhpSpecies());

      await waitFor(() => expect(result.current.isLoading).toBe(false));
      expect(result.current.speciesList.length).toBe(1);
      expect(result.current.error).toBe(null);
      expect(result.current.speciesList[0].common_name).toBe("Common Tree");
    });
  });

  it("handles species fetch errors locally", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      statusText: "Unauthorised",
    });

    const { result } = renderHook(() => useAhpSpecies());

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toContain("Failed to fetch species");
    expect(result.current.speciesList).toEqual([]);
  });
});

describe("useAhpFactors", () => {
  it("wraps the flat array API response into the factors object", async () => {
    const mockFlatArray = ["Rainfall", "Temperature"];

    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockFlatArray,
    });

    const { result } = renderHook(() => useAhpFactors());

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.factorsList?.factors).toEqual([
      "Rainfall",
      "Temperature",
    ]);
    expect(result.current.error).toBe(null);
  });

  it("handles factors fetch errors locally", async () => {
    // Mock a 500 or 404 response
    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      statusText: "Internal Server Error",
    });

    const { result } = renderHook(() => useAhpFactors());

    // Wait for the hook to finish the async cycle
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    // Assert the local error state matches your catch block logic
    expect(result.current.error).toBe(
      "Could not load features: Internal Server Error"
    );
    expect(result.current.factorsList).toBe(null);
  });
});

describe("useAhpCalculation", () => {
  it("posts matrix payload and returns results", async () => {
    const mockResponse = {
      weights: { Rainfall: 0.8 },
      consistency_ratio: 0.05,
      is_consistent: true,
    };

    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useAhpCalculation());

    await act(async () => {
      await result.current.handleCalculate({
        species_id: 1,
        matrix: [
          [1, 3],
          [0.33, 1],
        ],
      });
    });

    expect(result.current.isCalculating).toBe(false);
    expect(result.current.results?.is_consistent).toBe(true);
    expect(result.current.error).toBe(null);
  });

  it("handles calculation errors correctly", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      statusText: "Bad Request",
      json: async () => ({ detail: "Matrix invalid" }),
    });

    const { result } = renderHook(() => useAhpCalculation());

    await act(async () => {
      await result.current.handleCalculate({ species_id: 1, matrix: [] });
    });

    expect(result.current.error).toBe("Calculation failed: Matrix invalid");
    expect(result.current.results).toBe(null);
  });
});
