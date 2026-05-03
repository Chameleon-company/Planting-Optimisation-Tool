import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  createSpecies,
  deleteSpecies,
  getAllSpecies,
  getSoilTextures,
  updateSpecies,
} from "../utils/speciesApi";

const speciesPayload = {
  name: "Test species",
  common_name: "Test common",
  rainfall_mm_min: 200,
  rainfall_mm_max: 500,
  temperature_celsius_min: 10,
  temperature_celsius_max: 30,
  elevation_m_min: 0,
  elevation_m_max: 100,
  ph_min: 5,
  ph_max: 7,
  coastal: false,
  riparian: false,
  nitrogen_fixing: false,
  shade_tolerant: false,
  bank_stabilising: false,
  soil_textures: [1],
  agroforestry_types: [1],
};

function mockJsonResponse(data: unknown, ok = true) {
  return {
    ok,
    json: vi.fn().mockResolvedValue(data),
  } as unknown as Response;
}

describe("speciesApi", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("gets all species", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse([]));

    const result = await getAllSpecies("test-token");

    expect(result).toEqual([]);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/species"),
      expect.objectContaining({
        headers: {
          Authorization: "Bearer test-token",
        },
      })
    );
  });

  it("creates species with auth token", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse({ id: 1, ...speciesPayload }));

    const result = await createSpecies(speciesPayload, "test-token");

    expect(result.id).toBe(1);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/species"),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
        }),
      })
    );
  });

  it("updates species with auth token", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse({ id: 1, ...speciesPayload }));

    const result = await updateSpecies(1, speciesPayload, "test-token");

    expect(result.id).toBe(1);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/species/1"),
      expect.objectContaining({
        method: "PUT",
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
        }),
      })
    );
  });

  it("deletes species with auth token", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue({ ok: true } as Response);

    await deleteSpecies(1, "test-token");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/species/1"),
      expect.objectContaining({
        method: "DELETE",
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
        }),
      })
    );
  });

  it("gets soil textures", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse([{ id: 1, name: "sand" }])
    );

    const result = await getSoilTextures();

    expect(result).toEqual([{ id: 1, name: "sand" }]);
  });

  it("throws API error message when request fails", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({ detail: "Validation failed" }, false)
    );

    await expect(getAllSpecies("test-token")).rejects.toThrow(
      "Validation failed"
    );
  });
});

it("formats backend validation detail arrays", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    mockJsonResponse(
      {
        detail: [
          { msg: "Temperature must be less than or equal to 50." },
          { msg: "pH must be between 0 and 14." },
        ],
      },
      false
    )
  );

  await expect(createSpecies(speciesPayload, "test-token")).rejects.toThrow(
    "Temperature must be less than or equal to 50. pH must be between 0 and 14."
  );
});

it("falls back when backend error format is unknown", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(mockJsonResponse({}, false));

  await expect(getAllSpecies("test-token")).rejects.toThrow("API error");
});
