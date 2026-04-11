// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { useAhpSpecies, useAhpFactors, useAhpCalculation } from "@/hooks/useAhp";


vi.mock('@/contexts/AuthContext', () => ({
    useAuth: () => ({
        token: 'fake-token',
        getAccessToken: vi.fn(() => 'fake-token')
    })
}));

const mockThrowAsyncError = vi.fn();
vi.mock('@/hooks/useAsyncError', () => ({
    useAsyncError: () => mockThrowAsyncError
}));

describe("AHP Hooks", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        global.fetch = vi.fn();
    });

    describe("useAhpSpecies", () => {
        it("fetches and returns species dropdown data", async () => {
            const mockData = [{ id: 1, name: "scientific", common_name: "Common Tree" }];

            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: async () => mockData
            });

            const { result } = renderHook(() => useAhpSpecies());

            await waitFor(() => expect(result.current.isLoading).toBe(false));
            expect(result.current.speciesList.length).toBe(1);
            expect(result.current.speciesList[0].common_name).toBe("Common Tree");
        });
    });

    describe("useAhpFactors", () => {
        it("wraps the flat array API response into the factors object", async () => {
            const mockFlatArray = ["Rainfall", "Temperature"];

            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: async () => mockFlatArray
            });

            const { result } = renderHook(() => useAhpFactors());

            await waitFor(() => expect(result.current.isLoading).toBe(false));
            expect(result.current.factorsList?.factors).toEqual(["Rainfall", "Temperature"]);
        });
    });

    describe("useAhpCalculation", () => {
        it("posts matrix payload and returns results", async () => {
            const mockResponse = { weights: { Rainfall: 0.8 }, consistency_ratio: 0.05, is_consistent: true };

            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: async () => mockResponse
            });

            const { result } = renderHook(() => useAhpCalculation());

            await act(async () => {
                await result.current.handleCalculate({ species_id: 1, matrix: [[1, 3], [0.33, 1]] });
            });

            expect(result.current.isCalculating).toBe(false);
            expect(result.current.results?.is_consistent).toBe(true);
        });

        it("handles calculation errors correctly", async () => {
            (global.fetch as any).mockResolvedValue({
                ok: false,
                statusText: "Bad Request",
                json: async () => ({ detail: "Matrix invalid" })
            });

            const { result } = renderHook(() => useAhpCalculation());

            await act(async () => {
                await result.current.handleCalculate({ species_id: 1, matrix: [] });
            });

            expect(mockThrowAsyncError).toHaveBeenCalledWith(new Error("Calculation failed: Matrix invalid"));
        });
    });
});