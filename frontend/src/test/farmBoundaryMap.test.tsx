// @vitest-environment jsdom
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import L from "leaflet";
import type { GeoJsonObject } from "geojson";

vi.mock("leaflet/dist/leaflet.css", () => ({}));

interface MockBounds {
  getNorth: () => number;
  getSouth: () => number;
  getEast: () => number;
  getWest: () => number;
}

vi.mock("react-leaflet", () => ({
  MapContainer: ({
    children,
    bounds,
  }: {
    children: React.ReactNode;
    bounds?: MockBounds;
  }) => (
    <div
      data-testid="map-container"
      data-bounds={
        bounds
          ? `${bounds.getNorth()},${bounds.getSouth()},${bounds.getEast()},${bounds.getWest()}`
          : ""
      }
    >
      {children}
    </div>
  ),
  TileLayer: () => null,
  GeoJSON: () => <div data-testid="geojson" />,
}));

vi.mock("leaflet", () => ({
  default: {
    geoJSON: vi.fn(() => ({
      getBounds: () => ({
        getNorth: () => -8.0,
        getSouth: () => -9.0,
        getEast: () => 127.0,
        getWest: () => 126.0,
      }),
    })),
  },
}));

import FarmBoundaryMap from "@/components/map/FarmBoundaryMap";

const BOUNDARY = { type: "FeatureCollection", features: [] } as GeoJsonObject;

describe("FarmBoundaryMap", () => {
  it("renders nothing when boundary is null and not loading", () => {
    render(<FarmBoundaryMap boundary={null} isLoading={false} error={null} />);
    expect(screen.queryByTestId("map-container")).not.toBeInTheDocument();
  });

  it("shows loading message while fetching", () => {
    render(<FarmBoundaryMap boundary={null} isLoading={true} error={null} />);
    expect(screen.getByText("Loading map...")).toBeInTheDocument();
    expect(screen.queryByTestId("map-container")).not.toBeInTheDocument();
  });

  it("shows error message when fetch fails", () => {
    render(
      <FarmBoundaryMap
        boundary={null}
        isLoading={false}
        error="Failed to load farm boundary."
      />
    );
    expect(
      screen.getByText("Failed to load farm boundary.")
    ).toBeInTheDocument();
    expect(screen.queryByTestId("map-container")).not.toBeInTheDocument();
  });

  it("renders the map container when a valid boundary is provided", () => {
    render(
      <FarmBoundaryMap boundary={BOUNDARY} isLoading={false} error={null} />
    );
    expect(screen.getByTestId("map-container")).toBeInTheDocument();
  });

  it("passes the calculated bounds to MapContainer so it auto-centres and zooms to the farm extent", () => {
    render(
      <FarmBoundaryMap boundary={BOUNDARY} isLoading={false} error={null} />
    );
    expect(screen.getByTestId("map-container")).toHaveAttribute(
      "data-bounds",
      "-8,-9,127,126"
    );
  });

  it("renders the boundary GeoJSON layer", () => {
    render(
      <FarmBoundaryMap boundary={BOUNDARY} isLoading={false} error={null} />
    );
    expect(screen.getByTestId("geojson")).toBeInTheDocument();
  });

  it("renders the Farm Boundary heading", () => {
    render(
      <FarmBoundaryMap boundary={BOUNDARY} isLoading={false} error={null} />
    );
    expect(screen.getByText("Farm Boundary")).toBeInTheDocument();
  });

  it("renders nothing when getBounds throws on an invalid boundary", () => {
    vi.mocked(L.geoJSON).mockImplementationOnce(() => {
      throw new Error("Invalid geometry");
    });
    render(
      <FarmBoundaryMap boundary={BOUNDARY} isLoading={false} error={null} />
    );
    expect(screen.queryByTestId("map-container")).not.toBeInTheDocument();
  });
});
