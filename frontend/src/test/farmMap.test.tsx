// @vitest-environment jsdom
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { GeoJsonObject } from "geojson";

vi.mock("leaflet/dist/leaflet.css", () => ({}));

vi.mock("react-leaflet", () => ({
  MapContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="map-container">{children}</div>
  ),
  TileLayer: () => null,
  GeoJSON: () => <div data-testid="geojson" />,
  Polyline: () => <div data-testid="polyline" />,
}));

vi.mock("leaflet", () => ({
  default: {
    geoJSON: vi.fn(() => ({
      getBounds: () => ({
        getCenter: () => ({ lat: -8.5, lng: 126.5 }),
        getNorth: () => -8.0,
        getSouth: () => -9.0,
        getEast: () => 127.0,
        getWest: () => 126.0,
      }),
    })),
    circleMarker: vi.fn(() => ({})),
  },
}));

import FarmMap from "@/components/calculator/FarmMap";

const BOUNDARY = { type: "FeatureCollection", features: [] } as GeoJsonObject;
const GRID = { type: "FeatureCollection", features: [] } as GeoJsonObject;

describe("FarmMap", () => {
  it("renders nothing when boundary is null", () => {
    render(<FarmMap boundary={null} grid={null} optimalAngle={null} />);
    expect(screen.queryByTestId("map-container")).not.toBeInTheDocument();
  });

  it("renders the map when a valid boundary is provided", () => {
    render(<FarmMap boundary={BOUNDARY} grid={null} optimalAngle={null} />);
    expect(screen.getByTestId("map-container")).toBeInTheDocument();
  });

  it("renders the boundary GeoJSON layer", () => {
    render(<FarmMap boundary={BOUNDARY} grid={null} optimalAngle={null} />);
    expect(screen.getByTestId("geojson")).toBeInTheDocument();
  });

  it("renders grid overlay lines when optimalAngle is set", () => {
    render(
      <FarmMap boundary={BOUNDARY} grid={null} optimalAngle={20} spacingY={3} />
    );
    expect(screen.getAllByTestId("polyline").length).toBeGreaterThan(0);
  });

  it("renders no polylines when optimalAngle is null", () => {
    render(<FarmMap boundary={BOUNDARY} grid={null} optimalAngle={null} />);
    expect(screen.queryAllByTestId("polyline").length).toBe(0);
  });

  it("renders a second GeoJSON layer when grid data is provided", () => {
    render(<FarmMap boundary={BOUNDARY} grid={GRID} optimalAngle={null} />);
    expect(screen.getAllByTestId("geojson").length).toBe(2);
  });
});
