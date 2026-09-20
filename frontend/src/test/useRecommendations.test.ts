import { describe, it, expect, vi, beforeEach, Mock } from "vitest";

import { renderHook, waitFor } from "@testing-library/react";
import { useRecommendations } from "@/hooks/useRecommendations";

describe("useRecommendations Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    localStorage.clear();
    localStorage.setItem("access_token", "fake-token");

    global.fetch = vi.fn();

    window.URL.createObjectURL = vi.fn(() => "blob:url");
    window.URL.revokeObjectURL = vi.fn();
  });

  it("fetches and returns recommendation data successfully", async () => {
    const mockData = {
      recommendations: [
        {
          species_id: 1,
          score_mcda: 0.9,
        },
      ],
      excluded_species: [
        {
          id: 2,
          reasons: [],
        },
      ],
    };

    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    const { result } = renderHook(() => useRecommendations("123"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/recommendations/123"),
      expect.objectContaining({
        method: "GET",
        headers: expect.any(Headers),
      })
    );

    const [, options] = (global.fetch as Mock).mock.calls[0];

    expect(options.headers.get("Authorization")).toBe("Bearer fake-token");

    expect(options.headers.get("Accept")).toBe("application/json");

    expect(result.current.recs.length).toBe(1);
    expect(result.current.excludes.length).toBe(1);
    expect(result.current.hasSearched).toBe(true);
  });

  it("does not fetch if farmId is empty", async () => {
    const { result } = renderHook(() => useRecommendations(""));

    expect(global.fetch).not.toHaveBeenCalled();
    expect(result.current.hasSearched).toBe(false);
  });

  it("shows an error when there is no access token", async () => {
    localStorage.removeItem("access_token");

    const { result } = renderHook(() => useRecommendations("123"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe("Please log in to continue.");

    expect(global.fetch).not.toHaveBeenCalled();
  });

  it("handles API errors by returning an error message", async () => {
    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      status: 500,
      json: () =>
        Promise.resolve({
          detail: "Internal Server Error",
        }),
    });

    const { result } = renderHook(() => useRecommendations("123"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe("Internal Server Error");

    expect(result.current.hasSearched).toBe(false);
  });

  it("triggers a PDF download successfully", async () => {
    const mockBlob = new Blob(["pdf-content"], {
      type: "application/pdf",
    });

    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      status: 200,
      blob: async () => mockBlob,
      json: async () => ({}),
    });

    const { result } = renderHook(() => useRecommendations("123"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const linkSpy = {
      click: vi.fn(),
      setAttribute: vi.fn(),
      remove: vi.fn(),
      style: {} as CSSStyleDeclaration,
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
      expect.objectContaining({
        method: "GET",
        headers: expect.any(Headers),
      })
    );

    const calls = (global.fetch as Mock).mock.calls;

    const pdfCall = calls.find(([url]) =>
      String(url).includes("/reports/farm/123/export/pdf")
    );

    expect(pdfCall).toBeDefined();

    const pdfOptions = pdfCall?.[1];

    expect(pdfOptions.headers.get("Authorization")).toBe("Bearer fake-token");

    expect(window.URL.createObjectURL).toHaveBeenCalledWith(mockBlob);

    expect(linkSpy.click).toHaveBeenCalled();

    createElementSpy.mockRestore();
    appendSpy.mockRestore();
  });
});
