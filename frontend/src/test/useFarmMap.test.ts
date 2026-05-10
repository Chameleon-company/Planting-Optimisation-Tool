// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useFarmMap } from "@/hooks/useFarmMap";

const stableGetAccessToken = vi.fn<() => string | null>(() => "fake-token");

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: stableGetAccessToken,
  }),
}));

const mockBoundary = {
  type: "Feature",
  geometry: { type: "MultiPolygon", coordinates: [] },
  properties: {},
};
const mockGrid = { type: "FeatureCollection", features: [] };

describe("useFarmMap", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it("does not fetch when farmId is null", () => {
    const { result } = renderHook(() => useFarmMap(null));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.boundary).toBe(null);
    expect(result.current.grid).toBe(null);
  });

  it("fetches boundary and grid in parallel and returns both", async () => {
    (global.fetch as Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockBoundary })
      .mockResolvedValueOnce({ ok: true, json: async () => mockGrid });

    const { result } = renderHook(() => useFarmMap(1));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(global.fetch).toHaveBeenCalledTimes(2);
    expect(result.current.boundary).toEqual(mockBoundary);
    expect(result.current.grid).toEqual(mockGrid);
    expect(result.current.error).toBe(null);
  });

  it("sets boundary to null when boundary fetch fails", async () => {
    (global.fetch as Mock)
      .mockResolvedValueOnce({ ok: false })
      .mockResolvedValueOnce({ ok: true, json: async () => mockGrid });

    const { result } = renderHook(() => useFarmMap(1));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.boundary).toBe(null);
    expect(result.current.grid).toEqual(mockGrid);
  });

  it("sets grid to null when grid fetch fails", async () => {
    (global.fetch as Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockBoundary })
      .mockResolvedValueOnce({ ok: false });

    const { result } = renderHook(() => useFarmMap(1));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.boundary).toEqual(mockBoundary);
    expect(result.current.grid).toBe(null);
    expect(result.current.error).toBe(null);
  });

  it("sets error on network failure", async () => {
    (global.fetch as Mock).mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useFarmMap(1));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe("Failed to load map data.");
    expect(result.current.boundary).toBe(null);
    expect(result.current.grid).toBe(null);
  });

  it("sets session expired error and does not fetch when token is missing", async () => {
    stableGetAccessToken.mockReturnValueOnce(null);

    const { result } = renderHook(() => useFarmMap(1));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.error).toBe(
      "Your session has expired. Please log in again."
    );
  });
});
