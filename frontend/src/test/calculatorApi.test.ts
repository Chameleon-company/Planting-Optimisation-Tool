// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { getSaplingEstimation } from "@/utils/calculatorApi";
import type {
  CalcParams,
  SaplingEstimationResponse,
} from "@/utils/calculatorApi";

const TOKEN = "test-token";
const PARAMS: CalcParams = { spacingX: 3.0, spacingY: 3.0, maxSlope: 15.0 };

const mockResponse: SaplingEstimationResponse = {
  status: "ok",
  farm_count: 2,
  results: [
    {
      farm_id: 1,
      status: "success",
      pre_slope_count: 100,
      aligned_count: 80,
      optimal_angle: 20,
    },
    {
      farm_id: 2,
      status: "failed",
      message: "No boundary data",
    },
  ],
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
        json: async () => mockResponse,
      });

      await getSaplingEstimation([42], PARAMS, TOKEN);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/sapling_estimation/calculate"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: `Bearer ${TOKEN}`,
            "Content-Type": "application/json",
          }),
        })
      );
    });

    it("sends farm_id and spacing params in the request body", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      await getSaplingEstimation([42], PARAMS, TOKEN);

      const body = JSON.parse(
        (global.fetch as Mock).mock.calls[0][1].body as string
      );
      expect(body).toEqual({
        farm_ids: [42],
        spacing_x: PARAMS.spacingX,
        spacing_y: PARAMS.spacingY,
        max_slope: PARAMS.maxSlope,
      });
    });

    it("forwards every requested farm id as an array", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      await getSaplingEstimation([1, 2, 3], PARAMS, TOKEN);

      const body = JSON.parse(
        (global.fetch as Mock).mock.calls[0][1].body as string
      );
      expect(body.farm_ids).toEqual([1, 2, 3]);
    });

    it("returns the parsed batch response on success", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      const response = await getSaplingEstimation([1, 2], PARAMS, TOKEN);

      expect(response).toEqual(mockResponse);
      expect(response.results).toHaveLength(2);
      expect(response.results[0].status).toBe("success");
      expect(response.results[1].status).toBe("failed");
    });

    it("throws the API error message on non-ok response", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        json: async () => ({ detail: "Farm not found" }),
      });

      await expect(getSaplingEstimation([42], PARAMS, TOKEN)).rejects.toThrow(
        "Farm not found"
      );
    });

    it("throws a fallback message when error response has no message field", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        json: async () => ({}),
      });

      await expect(getSaplingEstimation([42], PARAMS, TOKEN)).rejects.toThrow(
        "Failed to fetch estimation"
      );
    });
  });
});
