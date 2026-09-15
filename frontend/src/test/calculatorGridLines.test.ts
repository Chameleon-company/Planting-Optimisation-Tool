// @vitest-environment jsdom
import { describe, it, expect } from "vitest";
import L from "leaflet";
import { computeGridLines } from "@/utils/calculatorGridLines";

const bounds = L.latLngBounds([
  [10.0, 20.0],
  [10.002, 20.003],
]);

const midpoint = (line: [number, number][]) =>
  [(line[0][0] + line[1][0]) / 2, (line[0][1] + line[1][1]) / 2] as const;

describe("computeGridLines", () => {
  it("returns lines made of two [lat, lng] points", () => {
    const lines = computeGridLines(bounds, 30, 3);
    expect(lines.length).toBeGreaterThan(0);
    for (const line of lines) {
      expect(line).toHaveLength(2);
      for (const point of line) {
        expect(point).toHaveLength(2);
        expect(Number.isFinite(point[0])).toBe(true);
        expect(Number.isFinite(point[1])).toBe(true);
      }
    }
  });

  it("draws horizontal rows at 0° (endpoints share a latitude)", () => {
    const [line] = computeGridLines(bounds, 0, 3);
    expect(Math.abs(line[0][0] - line[1][0])).toBeLessThan(1e-9);
    expect(Math.abs(line[0][1] - line[1][1])).toBeGreaterThan(1e-4);
  });

  it("draws vertical rows at 90° (endpoints share a longitude)", () => {
    const [line] = computeGridLines(bounds, 90, 3);
    expect(Math.abs(line[0][1] - line[1][1])).toBeLessThan(1e-9);
    expect(Math.abs(line[0][0] - line[1][0])).toBeGreaterThan(1e-4);
  });

  it("centres one row exactly on the field's centre point", () => {
    const center = bounds.getCenter();
    const lines = computeGridLines(bounds, 45, 3);
    const hasCentreRow = lines.some(line => {
      const [lat, lng] = midpoint(line);
      return (
        Math.abs(lat - center.lat) < 1e-9 && Math.abs(lng - center.lng) < 1e-9
      );
    });
    expect(hasCentreRow).toBe(true);
  });

  it("produces more rows as the spacing shrinks", () => {
    const smallgaps = computeGridLines(bounds, 0, 1);
    const largegaps = computeGridLines(bounds, 0, 10);
    expect(smallgaps.length).toBeGreaterThan(largegaps.length);
  });
});
