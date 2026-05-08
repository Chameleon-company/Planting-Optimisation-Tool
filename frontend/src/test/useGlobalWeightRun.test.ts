// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { useGlobalWeightRuns } from "@/hooks/useGlobalWeightRuns";

const stableGetAccessToken = vi.fn(() => "fake-token");

vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: stableGetAccessToken,
  }),
}));

describe("useGlobalWeightRuns", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it("fetches runs automatically on mount", async () => {
    const mockRuns = [
      { id: "1", filename: "test.csv", created_at: "2026-01-01" },
    ];

    (global.fetch as Mock).mockResolvedValue({
      ok: true,
      json: async () => mockRuns,
    });

    const { result } = renderHook(() => useGlobalWeightRuns());

    // Should initially be loading
    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.runs).toEqual(mockRuns);
    expect(result.current.error).toBe(null);
  });

  describe("uploadCsv", () => {
    it("uploads a file and refreshes the list on success", async () => {
      const mockFile = new File(["data"], "test.csv", { type: "text/csv" });

      // First fetch (on mount)
      (global.fetch as Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [],
        })
        // Upload call
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: "success", run_id: "123" }),
        })
        // Refresh call
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [{ id: "123", filename: "test.csv" }],
        });

      const { result } = renderHook(() => useGlobalWeightRuns());

      await act(async () => {
        await result.current.uploadCsv(mockFile);
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/global-weights/import"),
        expect.objectContaining({
          method: "POST",
          body: expect.any(FormData),
        })
      );
      expect(result.current.runs.length).toBe(1);
    });
  });

  describe("Error Handling (extractErrorMessage)", () => {
    it("handles standard FastAPI HTTPException strings", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ detail: "Invalid file format" }),
      });

      const { result } = renderHook(() => useGlobalWeightRuns());

      await waitFor(() => expect(result.current.isLoading).toBe(false));
      expect(result.current.error).toBe("Invalid file format");
    });

    it("handles Pydantic 422 validation arrays", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({
          detail: [
            { msg: "Field required" },
            { msg: "Must be greater than 0" },
          ],
        }),
      });

      const { result } = renderHook(() => useGlobalWeightRuns());

      await waitFor(() => expect(result.current.isLoading).toBe(false));
      expect(result.current.error).toBe(
        "Field required | Must be greater than 0"
      );
    });

    it("handles non-JSON server errors (500)", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        status: 500,
        // Mock json() to throw, simulating a non-JSON response like an HTML crash page
        json: async () => {
          throw new Error("Not JSON");
        },
      });

      const { result } = renderHook(() => useGlobalWeightRuns());

      await waitFor(() => expect(result.current.isLoading).toBe(false));
      expect(result.current.error).toContain("Server Error (500)");
    });
  });

  describe("deleteRun", () => {
    it("deletes a run and refreshes the list", async () => {
      (global.fetch as Mock)
        .mockResolvedValueOnce({ ok: true, json: async () => [] }) // Mount
        .mockResolvedValueOnce({ ok: true }); // Delete call

      const { result } = renderHook(() => useGlobalWeightRuns());

      await act(async () => {
        await result.current.deleteRun("123");
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/global-weights/runs/123"),
        expect.objectContaining({ method: "DELETE" })
      );
    });
  });
});
