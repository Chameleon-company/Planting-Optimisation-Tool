import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useRecommendations } from "@/hooks/useRecommendations";

// Create a stable function reference outside the mock call
const stableGetAccessToken = vi.fn(() => "fake-token");

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: stableGetAccessToken, // Reference the stable function
  }),
}));

describe("useRecommendations Hook", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.resetModules();
    global.fetch = vi.fn();

    // Mock URL methods for PDF download
    window.URL.createObjectURL = vi.fn(() => "blob:url");
    window.URL.revokeObjectURL = vi.fn();
  });

  it("fetches and returns recommendation data successfully", async () => {
    const mockData = {
      recommendations: [{ species_id: 1, score_mcda: 0.9 }],
      excluded_species: [{ id: 2, reasons: [] }],
    };

    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { result } = renderHook(() => useRecommendations("123"));

    // Wait until loading finishes
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/recommendations/123"),
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({
          Authorization: "Bearer fake-token",
          Accept: "application/json",
        }),
      })
    );

    // Validate returned data
    expect(result.current.recs.length).toBe(1);
    expect(result.current.excludes.length).toBe(1);
    expect(result.current.hasSearched).toBe(true);
  });

  it("does not fetch if farmId is empty", async () => {
    const { result } = renderHook(() => useRecommendations(""));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.hasSearched).toBe(false);
  });

  it("handles API errors by returning an error message", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: "Internal Server Error" }),
    });

    const { result } = renderHook(() => useRecommendations("123"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe("Internal Server Error");
    expect(result.current.hasSearched).toBe(false);
  });

  it("triggers a PDF download successfully", async () => {
    const mockBlob = new Blob(["pdf-content"], { type: "application/pdf" });
    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      blob: async () => mockBlob,
    });

    // farmId to trigger the hook and get the function
    const { result } = renderHook(() => useRecommendations("123"));

    // Create a spy on document.createElement to catch the anchor tag
    const linkSpy = {
      click: vi.fn(),
      setAttribute: vi.fn(),
      remove: vi.fn(),
      style: {} as CSSStyleDeclaration,
      parentNode: {
        removeChild: vi.fn(),
      },
    } as unknown as HTMLAnchorElement;

    const createElementSpy = vi
      .spyOn(document, "createElement")
      .mockReturnValue(linkSpy);

    const appendSpy = vi
      .spyOn(document.body, "appendChild")
      .mockImplementation(node => {
        return node as Node;
      });

    await result.current.downloadPdf();

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/reports/farm/123/export/pdf"),
      expect.objectContaining({ method: "GET" })
    );
    expect(window.URL.createObjectURL).toHaveBeenCalledWith(mockBlob);
    expect(linkSpy.click).toHaveBeenCalled();

    createElementSpy.mockRestore();
    appendSpy.mockRestore();
  });
});
