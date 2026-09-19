// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import type { GeoJsonObject } from "geojson";

// Page to test
import ProfilePage from "../pages/ProfilePage";

vi.mock("leaflet/dist/leaflet.css", () => ({}));

vi.mock("react-leaflet", () => ({
  MapContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="map-container">{children}</div>
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

const mockUseSearchProfiles = vi.fn();
const mockUseFarmBoundary = vi.fn();

vi.mock("../hooks/useSearchProfiles", () => ({
  useSearchProfiles: (...args: unknown[]) => mockUseSearchProfiles(...args),
}));

vi.mock("@/hooks/useFarmBoundary", () => ({
  useFarmBoundary: (...args: unknown[]) => mockUseFarmBoundary(...args),
}));

vi.mock("../hooks/useUserProfiles", () => ({
  useUserProfiles: () => ({
    farms: [],
    isLoading: false,
    error: null,
    page: 0,
    setPage: vi.fn(),
    totalPages: 0,
    totalFarms: 0,
  }),
}));

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    user: { name: "John", role: "admin" },
    getAccessToken: () => "fake-token",
  }),
}));

const BOUNDARY: GeoJsonObject = {
  type: "FeatureCollection",
  features: [],
} as GeoJsonObject;

describe("ProfilePage", () => {
  beforeEach(() => {
    mockUseSearchProfiles.mockReturnValue({
      profile: null,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      replaceProfile: vi.fn(),
    });
    mockUseFarmBoundary.mockReturnValue({
      boundary: null,
      isLoading: false,
      error: null,
    });
  });

  it("renders the page title", () => {
    render(
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    );
    expect(screen.getByText("Environmental Profile")).toBeInTheDocument();
  });

  it("renders the farmer name in the header", () => {
    render(
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    );
    expect(screen.getByText(/John/i)).toBeInTheDocument();
  });

  it("renders the search input", () => {
    render(
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    );
    expect(
      screen.getByPlaceholderText(/search by farm id/i)
    ).toBeInTheDocument();
  });

  it("renders the empty farms state when user has no farms", () => {
    render(
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    );
    expect(screen.getByText(/no farms found/i)).toBeInTheDocument();
  });

  it("renders the farm boundary map when a profile is loaded", () => {
    mockUseSearchProfiles.mockReturnValue({
      profile: { id: 1, name: "Farm #1" },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      replaceProfile: vi.fn(),
    });
    mockUseFarmBoundary.mockReturnValue({
      boundary: BOUNDARY,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    );

    expect(screen.getByTestId("map-container")).toBeInTheDocument();
  });

  it("does not render the farm boundary map when no profile is loaded", () => {
    render(
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    );
    expect(screen.queryByTestId("map-container")).not.toBeInTheDocument();
  });
});
