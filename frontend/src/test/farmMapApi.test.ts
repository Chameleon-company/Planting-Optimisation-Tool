// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { getFarmBoundary, getPlantingGrid } from "@/utils/farmMapApi";

const TOKEN = "test-token";

describe("farmMapApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  describe("getFarmBoundary", () => {
    it("fetches from the correct URL with auth header", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ type: "Feature" }),
      });

      await getFarmBoundary(42, TOKEN);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/farms/42/boundary"),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${TOKEN}`,
          }),
        })
      );
    });

    it("throws on non-ok response", async () => {
      (global.fetch as Mock).mockResolvedValue({ ok: false });

      await expect(getFarmBoundary(42, TOKEN)).rejects.toThrow(
        "Failed to fetch boundary"
      );
    });
  });

  describe("getPlantingGrid", () => {
    it("fetches from the correct URL with auth header", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ type: "FeatureCollection", features: [] }),
      });

      await getPlantingGrid(42, TOKEN);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/sapling_estimation/42/grid"),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${TOKEN}`,
          }),
        })
      );
    });

    it("throws on non-ok response", async () => {
      (global.fetch as Mock).mockResolvedValue({ ok: false });

      await expect(getPlantingGrid(42, TOKEN)).rejects.toThrow(
        "Failed to fetch grid"
      );
    });
  });
});
