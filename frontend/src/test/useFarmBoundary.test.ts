// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useFarmBoundary } from "@/hooks/useFarmBoundary";

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

describe("useFarmBoundary", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it("does not fetch when farmId is null", () => {
    const { result } = renderHook(() => useFarmBoundary(null));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.boundary).toBe(null);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it("fetches boundary and returns it", async () => {
    (global.fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBoundary,
    });

    const { result } = renderHook(() => useFarmBoundary(1));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(result.current.boundary).toEqual(mockBoundary);
    expect(result.current.error).toBe(null);
  });

  it("fetches from the correct endpoint", async () => {
    (global.fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBoundary,
    });

    renderHook(() => useFarmBoundary(42));

    await waitFor(() =>
      expect(global.fetch).toHaveBeenCalledWith(
        "http://127.0.0.1:8080/farms/42/boundary",
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer fake-token",
          }),
        })
      )
    );
  });

  it("sets error when fetch returns non-ok response", async () => {
    (global.fetch as Mock).mockResolvedValueOnce({ ok: false });

    const { result } = renderHook(() => useFarmBoundary(1));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.boundary).toBe(null);
    expect(result.current.error).toBe("Failed to load farm boundary.");
  });

  it("sets error on network failure", async () => {
    (global.fetch as Mock).mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useFarmBoundary(1));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.boundary).toBe(null);
    expect(result.current.error).toBe("Failed to load farm boundary.");
  });

  it("does not fetch and sets error when token is missing", async () => {
    stableGetAccessToken.mockReturnValueOnce(null);

    const { result } = renderHook(() => useFarmBoundary(1));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.error).toBe("Please log in to continue.");
  });

  it("resets boundary and error when farmId changes to null", async () => {
    (global.fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBoundary,
    });

    const { result, rerender } = renderHook(({ id }) => useFarmBoundary(id), {
      initialProps: { id: 1 as number | null },
    });

    await waitFor(() => expect(result.current.boundary).toEqual(mockBoundary));

    rerender({ id: null });

    expect(result.current.boundary).toBe(null);
    expect(result.current.error).toBe(null);
  });
});
