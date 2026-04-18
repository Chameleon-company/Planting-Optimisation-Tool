// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useSearchProfiles } from "@/hooks/useSearchProfiles";

// Mock Data
const mockProfile = (id: number) => ({
  id,
  elevation_m: 149,
  ph: 6.5,
  slope: 4.2,
  latitude: -37.12345,
  longitude: 144.12345,
  area_ha: 0.402,
  coastal: true,
});

// Mock Functions
const mockGetAccessToken = vi.fn();
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({ getAccessToken: mockGetAccessToken }),
}));

// useSearchProfiles Tests
describe("useSearchProfiles Hook", () => {
  // Before each test clear all mock functions, set mock get access token to fake,
  // and map global.fetch to a mock function
  let mockFetch: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();
    mockGetAccessToken.mockReturnValue("fake-token");
    mockFetch = vi.fn();
    global.fetch = mockFetch;
  });

  it("fetches and returns a profile successfully when given a valid query", async () => {
    // Create a mock profile to return from the API
    const mockData = mockProfile(42);
    // Configure fetch to return a successful response with the mock profile
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    } as Response);

    // Render the hook with a valid query string matching the profile ID
    const { result } = renderHook(() => useSearchProfiles("42"));

    // Wait for loading to complete before asserting
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Expect fetch to have been called with the correct profile endpoint and auth header
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/profile/42"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer fake-token",
        }),
      })
    );

    // Expect the returned profile to match the mock data
    expect(result.current.profile).toMatchObject({ id: 42, elevation_m: 149 });
    expect(result.current.error).toBe(null);
  });

  it("does not fetch if query is empty string", async () => {
    // Render with an empty query useSearchProfiles the hook should skip the fetch entirely
    const { result } = renderHook(() => useSearchProfiles(""));

    // Expect no call to have been made and profile to remain null
    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.profile).toBe(null);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it("does not fetch if query is only whitespace", async () => {
    // Queries with only spaces should be treated the same as empty useSearchProfiles no fetch
    const { result } = renderHook(() => useSearchProfiles("   "));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.profile).toBe(null);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it("does not fetch if token is null", async () => {
    // Without an auth token the hook should stop before making any request
    mockGetAccessToken.mockReturnValue(null);

    const { result } = renderHook(() => useSearchProfiles("42"));

    // Expect no fetch call and a clean state
    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.profile).toBe(null);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it("refetches when query changes", async () => {
    // Stub fetch to return an empty successful response for both calls
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockProfile(1),
    } as Response);

    vi.stubGlobal("fetch", mockFetch);

    // Start with query "1" and capture the rerender function
    let query = "1";
    const { rerender } = renderHook(() => useSearchProfiles(query));

    // Wait for the first fetch triggered by query "1"
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    // Change the query to "2" and re-render the hook
    query = "2";
    rerender();

    // The hook should detect the query change and fire a second fetch
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  it("refetches when token changes", async () => {
    // Stub fetch to always return a successful empty-profile response
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockProfile(5),
    } as Response);

    vi.stubGlobal("fetch", mockFetch);

    let token = "token-1";
    mockGetAccessToken.mockImplementation(() => token);

    // Render with an initial token
    const { rerender } = renderHook(() => useSearchProfiles("5"));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    // Swap to a new token and trigger a re-render
    token = "token-2";
    rerender();

    // The hook should respond to the token change and fetch again
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  it("handles API errors with a detail string and sets error state", async () => {
    // Return a 404 response containing a detail message
    mockFetch.mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ detail: "Profile not found" }),
    } as Response);

    const { result } = renderHook(() => useSearchProfiles("99"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Expect the hook to show the detail message as the error
    expect(result.current.error).toBe("Profile not found");
    expect(result.current.profile).toBe(null);
  });

  it("handles non-Error objects thrown during fetch", async () => {
    // Mock fetch rejecting with a plain string rather than an Error instance
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockRejectedValue(
      "Unexpected string error"
    );

    const { result } = renderHook(() => useSearchProfiles("42"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Expect the fallback error message for non-Error thrown values
    expect(result.current.error).toBe("Unexpected error");
    expect(result.current.profile).toBe(null);
  });

  it("clears profile and error when query is cleared after a successful fetch", async () => {
    // First, return a successful profile
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockProfile(1),
    } as Response);

    let query = "1";
    const { result, rerender } = renderHook(() => useSearchProfiles(query));

    await waitFor(() => {
      expect(result.current.profile).not.toBe(null);
    });

    // Now clear the query useSearchProfiles the hook should reset
    query = "";
    rerender();

    expect(result.current.profile).toBe(null);
    expect(result.current.error).toBe(null);
  });
});
