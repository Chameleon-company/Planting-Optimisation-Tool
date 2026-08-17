// @vitest-environment jsdom
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useSearchProfiles } from "@/hooks/useSearchProfiles";
import type { Farm } from "@/hooks/useUserProfiles";

const { mockGetAccessToken } = vi.hoisted(() => ({
  mockGetAccessToken: vi.fn(),
}));

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: mockGetAccessToken,
  }),
}));

const fetchMock = vi.fn();

function createResponse(
  ok: boolean,
  status: number,
  body?: unknown,
  rejectJson = false
): Response {
  return {
    ok,
    status,
    json: rejectJson
      ? vi.fn().mockRejectedValue(new Error("Invalid JSON"))
      : vi.fn().mockResolvedValue(body),
  } as unknown as Response;
}

function createFarm(id: number, rainfall = 800): Farm {
  return {
    id,
    rainfall_mm: rainfall,
    temperature_celsius: 22,
    elevation_m: 150,
    ph: 6.5,
    soil_texture: { name: "Loam" },
    area_ha: 12.345,
    latitude: -37.12345,
    longitude: 144.12345,
    coastal: true,
    riparian: false,
    nitrogen_fixing: true,
    shade_tolerant: false,
    bank_stabilising: false,
    slope: 3.75,
    agroforestry_type: [],
  } as Farm;
}

describe("useSearchProfiles additional coverage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetAccessToken.mockReturnValue("test-token");
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("uses the API detail when loading a profile fails", async () => {
    fetchMock.mockResolvedValue(
      createResponse(false, 404, {
        detail: "Farm profile was not found.",
      })
    );

    const { result } = renderHook(() => useSearchProfiles("42"));

    await waitFor(() => {
      expect(result.current.error).toBe("Farm profile was not found.");
    });

    expect(result.current.profile).toBeNull();
    expect(result.current.isLoading).toBe(false);
  });

  it("uses a fallback message when the error is not JSON", async () => {
    fetchMock.mockResolvedValue(createResponse(false, 500, undefined, true));

    const { result } = renderHook(() => useSearchProfiles("42"));

    await waitFor(() => {
      expect(result.current.error).toBe("Failed to load profile (500)");
    });

    expect(result.current.profile).toBeNull();
  });

  it("adds the queried farm ID when the response does not contain one", async () => {
    const responseFarm = createFarm(42);
    const farmWithoutId = { ...responseFarm } as Partial<Farm>;
    delete farmWithoutId.id;

    fetchMock.mockResolvedValue(createResponse(true, 200, farmWithoutId));

    const { result } = renderHook(() => useSearchProfiles("42"));

    await waitFor(() => {
      expect(result.current.profile?.id).toBe(42);
    });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/farms/42"),
      expect.objectContaining({
        headers: {
          Authorization: "Bearer test-token",
          Accept: "application/json",
        },
      })
    );
  });

  it("refetches the current profile", async () => {
    fetchMock
      .mockResolvedValueOnce(createResponse(true, 200, createFarm(42, 800)))
      .mockResolvedValueOnce(createResponse(true, 200, createFarm(42, 1200)));

    const { result } = renderHook(() => useSearchProfiles("42"));

    await waitFor(() => {
      expect(result.current.profile?.rainfall_mm).toBe(800);
    });

    await act(async () => {
      await result.current.refetch();
    });

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(result.current.profile?.rainfall_mm).toBe(1200);
  });

  it("replaces the currently displayed profile", () => {
    const replacement = createFarm(42, 1600);

    const { result } = renderHook(() => useSearchProfiles(""));

    act(() => {
      result.current.replaceProfile(replacement);
    });

    expect(result.current.profile).toEqual(replacement);
    expect(result.current.error).toBeNull();
  });

  it("clears the profile when there is no access token", async () => {
    mockGetAccessToken.mockReturnValue(null);

    const { result } = renderHook(() => useSearchProfiles("42"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.profile).toBeNull();
    expect(result.current.error).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
