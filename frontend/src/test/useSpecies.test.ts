// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";

// Hook to test
import { useSpecies } from "@/hooks/useSpecies";

// Mock Contentful client
import { client } from "@/utils/contentfulClient";

// Mock Setup
vi.mock("@/utils/contentfulClient", () => ({
  client: {
    getEntries: vi.fn(),
  },
}));

const mockedGetEntries = vi.mocked(client.getEntries);

describe("useSpecies Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetches and returns species data successfully", async () => {
    const mockData = {
      items: [
        {
          sys: { id: "1" },
          fields: {
            name: "Test Tree",
            description: { content: [] },
          },
        },
      ],
    };

    // Mock API response
    mockedGetEntries.mockResolvedValue(
      mockData as unknown as Awaited<ReturnType<typeof client.getEntries>>
    );

    const { result } = renderHook(() => useSpecies("Test"));

    // Wait until data is loaded
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Validate returned data
    expect(result.current.species.length).toBe(1);
    expect(result.current.error).toBeNull();
  });

  it("handles empty results correctly", async () => {
    const mockData = {
      items: [],
    };

    mockedGetEntries.mockResolvedValue(
      mockData as unknown as Awaited<ReturnType<typeof client.getEntries>>
    );

    const { result } = renderHook(() => useSpecies("Nothing"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Should return empty array
    expect(result.current.species.length).toBe(0);
    expect(result.current.error).toBeNull();
  });

  it("handles API errors gracefully", async () => {
    mockedGetEntries.mockRejectedValue(new Error("API Error"));

    const { result } = renderHook(() => useSpecies("Fail"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Should capture error
    expect(result.current.error).not.toBeNull();
    expect(result.current.species.length).toBe(0);
  });

  it("sets loading state correctly", async () => {
    let resolveFn!: (
      value: Awaited<ReturnType<typeof client.getEntries>>
    ) => void;

    // Create a pending promise
    mockedGetEntries.mockReturnValue(
      new Promise(resolve => {
        resolveFn = resolve;
      })
    );

    const { result } = renderHook(() => useSpecies("Loading"));

    // Initially loading should be true
    expect(result.current.isLoading).toBe(true);

    // Resolve API call
    resolveFn({ items: [] } as unknown as Awaited<
      ReturnType<typeof client.getEntries>
    >);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
  });

  it("re-fetches data when query changes", async () => {
    // Mock API to return empty for both calls
    mockedGetEntries.mockResolvedValue({ items: [] } as unknown as Awaited<
      ReturnType<typeof client.getEntries>
    >);

    // Render hook with initial query
    const { rerender } = renderHook(({ q }) => useSpecies(q), {
      initialProps: { q: "first" },
    });

    // Wait for first fetch to complete
    await waitFor(() => {
      expect(mockedGetEntries).toHaveBeenCalledTimes(1);
    });

    // Change the query to trigger a re-fetch
    rerender({ q: "second" });

    // Expect API to have been called a second time with new query
    await waitFor(() => {
      expect(mockedGetEntries).toHaveBeenCalledTimes(2);
    });

    expect(mockedGetEntries).toHaveBeenLastCalledWith(
      expect.objectContaining({ query: "second" })
    );
  });
});
