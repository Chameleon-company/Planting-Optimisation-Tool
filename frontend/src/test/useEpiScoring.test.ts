import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useEpiScoring } from "@/hooks/useEpiScoring";

const stableGetAccessToken = vi.fn(() => "fake-token");

vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: stableGetAccessToken,
  }),
}));

describe("useEpiScoring", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();

    // Mock URL methods for blob handling
    global.URL.createObjectURL = vi.fn(() => "blob:mock-url");
    global.URL.revokeObjectURL = vi.fn();

    // Mock document.createElement for anchor tag logic
    vi.spyOn(document, "createElement");
  });

  it("successfully processes EPI CSV and triggers download", async () => {
    const mockFile = new File(["test content"], "test.csv", {
      type: "text/csv",
    });
    const mockBlob = new Blob(["processed content"], { type: "text/csv" });

    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      blob: async () => mockBlob,
      headers: new Headers({
        "Content-Disposition": 'attachment; filename="custom_output.csv"',
      }),
    });

    const { result } = renderHook(() => useEpiScoring());

    await act(async () => {
      await result.current.processEpiCsv(mockFile);
    });

    // Verify loading states
    expect(result.current.isEpiLoading).toBe(false);
    expect(result.current.epiError).toBe(null);

    // Verify fetch call
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/global-weights/epi-add-scores"),
      expect.objectContaining({
        method: "POST",
        headers: { Authorization: "Bearer fake-token" },
        body: expect.any(FormData),
      })
    );

    // Verify download trigger
    expect(global.URL.createObjectURL).toHaveBeenCalledWith(mockBlob);
    expect(global.URL.revokeObjectURL).toHaveBeenCalledWith("blob:mock-url");
  });

  it("handles API errors by extracting the error detail", async () => {
    const mockFile = new File(["test content"], "test.csv", {
      type: "text/csv",
    });

    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      json: async () => ({ detail: "Invalid CSV format" }),
    });

    const { result } = renderHook(() => useEpiScoring());

    await act(async () => {
      await result.current.processEpiCsv(mockFile);
    });

    expect(result.current.isEpiLoading).toBe(false);
    expect(result.current.epiError).toBe("Invalid CSV format");
  });

  it("falls back to default error message if detail is missing", async () => {
    const mockFile = new File(["test content"], "test.csv", {
      type: "text/csv",
    });

    (global.fetch as Mock).mockResolvedValue({
      ok: false,
      json: async () => ({}), // Empty error object
    });

    const { result } = renderHook(() => useEpiScoring());

    await act(async () => {
      await result.current.processEpiCsv(mockFile);
    });

    expect(result.current.epiError).toBe("Failed to process EPI CSV");
  });

  it("handles network/unexpected errors", async () => {
    const mockFile = new File(["test content"], "test.csv", {
      type: "text/csv",
    });

    (global.fetch as Mock).mockRejectedValue(new Error("Network Failure"));

    const { result } = renderHook(() => useEpiScoring());

    await act(async () => {
      await result.current.processEpiCsv(mockFile);
    });

    expect(result.current.epiError).toBe("Network Failure");
    expect(result.current.isEpiLoading).toBe(false);
  });
});
