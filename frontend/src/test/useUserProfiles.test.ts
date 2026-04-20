// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { useUserProfiles } from "@/hooks/useUserProfiles";

// Mock Data
const mockFarm = (id: number) => ({
  id,
  rainfall_mm: 800,
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
  agroforestry_type: [{ name: "Silvopasture" }],
});

// Mock Functions
const mockGetAccessToken = vi.fn();
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({ getAccessToken: mockGetAccessToken }),
}));

// useUserProfiles Tests
describe("useUserProfiles Hook", () => {
  // Before each test clear all mock functions, set mock get access token to fake, and map
  // global.fetch to a mock function
  let mockFetch: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();
    mockGetAccessToken.mockReturnValue("fake-token");
    mockFetch = vi.fn();
    global.fetch = mockFetch;
  });

  it("fetches and returns farm data successfully", async () => {
    // Create two mock farms to simulate a real API response
    const mockData = [mockFarm(1), mockFarm(2)];
    // Configure fetch to return a successful HTTP response with the mock farm array
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    } as Response);

    // Render the hook and capture the result
    const { result } = renderHook(() => useUserProfiles());

    // Wait for the loading state to clear before asserting on the data
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Expect fetch to have been called with the correct user items and auth token
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/auth/users/me/items"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer fake-token",
        }),
      })
    );

    // Expect the returned data to match the two mock farms created
    expect(result.current.farms).toHaveLength(2);
    expect(result.current.totalFarms).toBe(2);
    expect(result.current.error).toBe(null);
  });

  it("does not fetch if token is null", async () => {
    // Without a token the hook should skip the fetch entirely
    mockGetAccessToken.mockReturnValue(null);

    const { result } = renderHook(() => useUserProfiles());

    // Expect no call and a empty page
    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.farms).toHaveLength(0);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it("refetches when token changes", async () => {
    // Stub fetch to return a successful empty array for both fetches
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response);

    vi.stubGlobal("fetch", mockFetch);

    // Start with the first token value
    let token = "token-1";
    mockGetAccessToken.mockImplementation(() => token);

    // Render the hook and capture the rerender function
    const { rerender } = renderHook(() => useUserProfiles());

    // Wait for the first fetch triggered by the initial token
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    // Update to a new token and re-render
    token = "token-2";
    rerender();

    // Confirm the hook responded to the token change with a second fetch
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  it("handles API errors and sets error state", async () => {
    // Return a 500 response with a plain-text error
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      text: async () => "Internal Server Error",
    } as Response);

    const { result } = renderHook(() => useUserProfiles());

    // Wait for loading to finish so we can inspect the error state
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe("Internal Server Error");
    expect(result.current.farms).toHaveLength(0);
  });

  it("handles API errors without error text by using fallback message", async () => {
    // Return a response with an empty body to trigger the fallback error format
    mockFetch.mockResolvedValue({
      ok: false,
      status: 404,
      text: async () => "",
    } as Response);

    const { result } = renderHook(() => useUserProfiles());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Expect the fallback message
    expect(result.current.error).toBe("Failed to fetch farms (404)");
    expect(result.current.farms).toHaveLength(0);
  });

  it("navigate pages correctly with PAGE_SIZE of 9", async () => {
    // Create 20 farms to verify page navigaton splits the data correctly across pages
    const mockData = Array.from({ length: 20 }, (_, i) => mockFarm(i + 1));
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    } as Response);

    const { result } = renderHook(() => useUserProfiles());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Expect the first page to show 9 of 20 total farms across 3 pages, starting on page 0
    expect(result.current.farms).toHaveLength(9);
    expect(result.current.totalPages).toBe(3);
    expect(result.current.totalFarms).toBe(20);
    expect(result.current.page).toBe(0);
  });

  it("can change pages", async () => {
    // Create 20 farms so there are enough for a third partial page
    const mockData = Array.from({ length: 20 }, (_, i) => mockFarm(i + 1));
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    } as Response);

    const { result } = renderHook(() => useUserProfiles());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Navigate to the third page (index 2)
    act(() => {
      result.current.setPage(2);
    });

    // Expect page index to update and show the remaining 2 farms on the last page
    expect(result.current.page).toBe(2);
    expect(result.current.farms).toHaveLength(2);
  });

  it("handles empty farm list", async () => {
    // Return an empty array
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response);

    const { result } = renderHook(() => useUserProfiles());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Expect all counts to be zero and no error to be set
    expect(result.current.farms).toHaveLength(0);
    expect(result.current.totalFarms).toBe(0);
    expect(result.current.totalPages).toBe(0);
    expect(result.current.error).toBe(null);
  });

  it("handles non-Error objects thrown during fetch", async () => {
    // Reject with a plain string to test the non-Error fallback path
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockRejectedValue(
      "Unexpected string error"
    );

    const { result } = renderHook(() => useUserProfiles());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Expect the generic fallback message when the thrown value is not an Error instance
    expect(result.current.error).toBe("An unexpected error occurred");
    expect(result.current.farms).toHaveLength(0);
  });
});
