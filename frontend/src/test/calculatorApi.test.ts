// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { getSaplingEstimation } from "@/utils/calculatorApi";
import type { CalcParams } from "@/utils/calculatorApi";

const TOKEN = "test-token";
const PARAMS: CalcParams = { spacingX: 3.0, spacingY: 3.0, maxSlope: 15.0 };

const mockResult = {
  id: 1,
  pre_slope_count: 100,
  aligned_count: 80,
  optimal_angle: 20,
};

describe("calculatorApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  describe("getSaplingEstimation", () => {
    it("sends a POST to the correct URL with auth header", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResult,
      });

      await getSaplingEstimation(42, PARAMS, TOKEN);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/sapling_estimation/calculate"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: `Bearer ${TOKEN}`,
          }),
        })
      );
    });

    it("sends farm_id and spacing params in the request body", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResult,
      });

      await getSaplingEstimation(42, PARAMS, TOKEN);

      const body = JSON.parse(
        (global.fetch as Mock).mock.calls[0][1].body as string
      );
      expect(body).toEqual({
        farm_id: 42,
        spacing_x: PARAMS.spacingX,
        spacing_y: PARAMS.spacingY,
        max_slope: PARAMS.maxSlope,
      });
    });

    it("returns parsed result on success", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResult,
      });

      const result = await getSaplingEstimation(42, PARAMS, TOKEN);

      expect(result).toEqual(mockResult);
    });

    it("throws the API error message on non-ok response", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        json: async () => ({ detail: "Farm not found" }),
      });

      await expect(getSaplingEstimation(42, PARAMS, TOKEN)).rejects.toThrow(
        "Farm not found"
      );
    });

    it("throws a fallback message when error response has no message field", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        json: async () => ({}),
      });

      await expect(getSaplingEstimation(42, PARAMS, TOKEN)).rejects.toThrow(
        "Failed to fetch estimation"
      );
    });
  });
});
