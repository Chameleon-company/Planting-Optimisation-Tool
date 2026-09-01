import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  createDependency,
  createExclusionRule,
  deleteDependency,
  deleteExclusionRule,
  getAllDependencies,
  getAllExclusionRules,
  getDependencyById,
  getExclusionRuleById,
  updateDependency,
  updateExclusionRule,
} from "../utils/exclusionRulesApi";

const exclusionRule = {
  id: 1,
  species_id: 5,
  feature: "rainfall_mm",
  operator: "<" as const,
  value: 1000,
  reason: "Rainfall below survival threshold",
};

const dependency = {
  id: 2,
  focal_species_id: 5,
  required_partner_id: 8,
};

function mockJsonResponse(data: unknown, ok = true) {
  return {
    ok,
    json: vi.fn().mockResolvedValue(data),
  } as unknown as Response;
}

describe("exclusionRulesApi", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("gets all exclusion rules", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse([exclusionRule]));

    const result = await getAllExclusionRules("test-token");

    expect(result).toEqual([exclusionRule]);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/exclusion-rules"),
      {
        headers: {
          Authorization: "Bearer test-token",
        },
      }
    );
  });

  it("gets an exclusion rule by id", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse(exclusionRule));

    const result = await getExclusionRuleById(1, "test-token");

    expect(result).toEqual(exclusionRule);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/exclusion-rules/1"),
      {
        headers: {
          Authorization: "Bearer test-token",
        },
      }
    );
  });

  it("creates an exclusion rule", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse(exclusionRule));

    const payload = {
      species_id: 5,
      feature: "rainfall_mm",
      operator: "<" as const,
      value: 1000,
      reason: "Rainfall below survival threshold",
    };

    const result = await createExclusionRule(payload, "test-token");

    expect(result).toEqual(exclusionRule);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/exclusion-rules"),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer test-token",
        },
        body: JSON.stringify(payload),
      }
    );
  });

  it("updates an exclusion rule with PATCH", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        ...exclusionRule,
        value: 1200,
      })
    );

    const payload = {
      value: 1200,
      reason: "Updated threshold",
    };

    const result = await updateExclusionRule(1, payload, "test-token");

    expect(result.value).toBe(1200);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/exclusion-rules/1"),
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer test-token",
        },
        body: JSON.stringify(payload),
      }
    );
  });

  it("deletes an exclusion rule", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
    } as Response);

    await deleteExclusionRule(1, "test-token");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/exclusion-rules/1"),
      {
        method: "DELETE",
        headers: {
          Authorization: "Bearer test-token",
        },
      }
    );
  });

  it("gets all species dependencies", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse([dependency]));

    const result = await getAllDependencies("test-token");

    expect(result).toEqual([dependency]);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/species-dependencies"),
      {
        headers: {
          Authorization: "Bearer test-token",
        },
      }
    );
  });

  it("gets a species dependency by id", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse(dependency));

    const result = await getDependencyById(2, "test-token");

    expect(result).toEqual(dependency);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/species-dependencies/2"),
      {
        headers: {
          Authorization: "Bearer test-token",
        },
      }
    );
  });

  it("creates a species dependency", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse(dependency));

    const payload = {
      focal_species_id: 5,
      required_partner_id: 8,
    };

    const result = await createDependency(payload, "test-token");

    expect(result).toEqual(dependency);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/species-dependencies"),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer test-token",
        },
        body: JSON.stringify(payload),
      }
    );
  });

  it("updates a species dependency with PATCH", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        ...dependency,
        required_partner_id: 9,
      })
    );

    const payload = {
      required_partner_id: 9,
    };

    const result = await updateDependency(2, payload, "test-token");

    expect(result.required_partner_id).toBe(9);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/species-dependencies/2"),
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer test-token",
        },
        body: JSON.stringify(payload),
      }
    );
  });

  it("deletes a species dependency", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
    } as Response);

    await deleteDependency(2, "test-token");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/species-dependencies/2"),
      {
        method: "DELETE",
        headers: {
          Authorization: "Bearer test-token",
        },
      }
    );
  });

  it("uses backend detail messages for API errors", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse(
        {
          detail: "Exclusion rule not found",
        },
        false
      )
    );

    await expect(getExclusionRuleById(999, "test-token")).rejects.toThrow(
      "Exclusion rule not found"
    );
  });

  it("formats backend validation detail arrays", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse(
        {
          detail: [
            {
              msg: "Species does not exist.",
            },
            {
              message: "Invalid rule value.",
            },
          ],
        },
        false
      )
    );

    await expect(
      createExclusionRule(
        {
          species_id: 999,
          feature: "rainfall_mm",
          operator: "<",
          value: 1000,
          reason: "Test",
        },
        "test-token"
      )
    ).rejects.toThrow("Species does not exist. Invalid rule value.");
  });

  it("falls back for an unknown backend error format", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({}, false)
    );

    await expect(getAllDependencies("test-token")).rejects.toThrow("API error");
  });

  it("handles delete API errors", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse(
        {
          detail: "Species dependency not found",
        },
        false
      )
    );

    await expect(deleteDependency(999, "test-token")).rejects.toThrow(
      "Species dependency not found"
    );
  });
});
