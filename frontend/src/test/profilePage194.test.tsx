// @vitest-environment jsdom
import type { ReactNode } from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { mockToastSuccess, mockToastError } = vi.hoisted(() => ({
  mockToastSuccess: vi.fn(),
  mockToastError: vi.fn(),
}));

vi.mock("react-hot-toast", () => ({
  default: {
    success: mockToastSuccess,
    error: mockToastError,
  },
}));

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

vi.mock("@/hooks/useFarmBoundary", () => ({
  useFarmBoundary: () => ({ boundary: null, isLoading: false, error: null }),
}));

import type { Farm } from "@/hooks/useUserProfiles";
import type { FarmUpdatePayload } from "@/hooks/useFarms";

import ProfilePage from "@/pages/ProfilePage";

const mocks = vi.hoisted(() => ({
  useUserProfiles: vi.fn(),
  useSearchProfiles: vi.fn(),
  useFarms: vi.fn(),
  useProfileActions: vi.fn(),
  refetch: vi.fn(),
  replaceProfile: vi.fn(),
  updateFarm: vi.fn(),
  regenerateProfile: vi.fn(),
  clearActionFeedback: vi.fn(),
}));

vi.mock("react-helmet-async", () => ({
  Helmet: ({ children }: { children?: ReactNode }) => <>{children}</>,
}));

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      id: 1,
      name: "Admin User",
      email: "admin@example.com",
      role: "admin",
      farms: [],
    },
    getAccessToken: () => "test-token",
  }),
}));

vi.mock("@/hooks/useUserProfiles", () => ({
  useUserProfiles: () => mocks.useUserProfiles(),
}));

vi.mock("@/hooks/useSearchProfiles", () => ({
  useSearchProfiles: (query: string) => mocks.useSearchProfiles(query),
}));

vi.mock("@/hooks/useFarms", () => ({
  useFarms: () => mocks.useFarms(),
}));

vi.mock("@/hooks/useProfileActions", () => ({
  useProfileActions: () => mocks.useProfileActions(),
}));

vi.mock("@/components/profile/profileHeader", () => ({
  default: ({
    userName,
    farmCount,
  }: {
    userName?: string;
    farmCount: number;
  }) => (
    <header>
      Environmental Profile - {userName} - {farmCount}
    </header>
  ),
}));

vi.mock("@/components/profile/profileFarms", () => ({
  default: () => <div data-testid="farm-list">Farm list</div>,
}));

interface SearchPanelProps {
  query: string;
  setQuery: (query: string) => void;
  profile: Farm | null;
  onEdit?: () => void;
  onRegenerate?: () => void;
  isRegenerating?: boolean;
  actionError?: string | null;
  actionMessage?: string | null;
}

vi.mock("@/components/profile/profileSearchPanel", () => ({
  default: ({
    query,
    setQuery,
    profile,
    onEdit,
    onRegenerate,
    isRegenerating,
    actionError,
    actionMessage,
  }: SearchPanelProps) => (
    <section>
      <div data-testid="current-query">{query}</div>

      <div data-testid="displayed-profile">
        {profile
          ? `${profile.id}:${profile.rainfall_mm}:${profile.soil_texture.name}`
          : "none"}
      </div>

      <button type="button" onClick={onEdit}>
        Panel Edit
      </button>

      <button type="button" onClick={onRegenerate}>
        {isRegenerating ? "Panel Regenerating" : "Panel Regenerate"}
      </button>

      <button type="button" onClick={() => setQuery("")}>
        Clear query
      </button>

      {actionMessage && <p data-testid="action-message">{actionMessage}</p>}

      {actionError && <p data-testid="action-error">{actionError}</p>}
    </section>
  ),
}));

interface EditModalProps {
  farm: Farm;
  onClose: () => void;
  onSuccess: (farmId: number, payload: FarmUpdatePayload) => Promise<void>;
}

vi.mock("@/components/farmManagement/farmsEditModal", () => ({
  default: ({ farm, onClose, onSuccess }: EditModalProps) => (
    <div role="dialog" aria-label="Edit farm modal">
      <span>Edit farm {farm.id}</span>

      <button
        type="button"
        onClick={() => {
          void onSuccess(farm.id, {
            rainfall_mm: 2000,
          }).catch(() => undefined);
        }}
      >
        Save modal
      </button>

      <button type="button" onClick={onClose}>
        Close modal
      </button>
    </div>
  ),
}));

const FARM: Farm = {
  id: 42,
  rainfall_mm: 800,
  temperature_celsius: 22,
  elevation_m: 150,
  ph: 6.5,
  soil_texture: { name: "Loam" },
  area_ha: 12.345,
  latitude: -37.12345,
  longitude: 144.12345,
  coastal: true,
  riparian: false,
  nitrogen_fixing: true,
  shade_tolerant: false,
  bank_stabilising: false,
  slope: 3.75,
  agroforestry_type: [],
} as Farm;

function renderPage(route = "/profile?farmId=42") {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <ProfilePage />
    </MemoryRouter>
  );
}

describe("ProfilePage #194 interactions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockToastSuccess.mockClear();
    mockToastError.mockClear();

    mocks.useUserProfiles.mockReturnValue({
      farms: [FARM],
      isLoading: false,
      error: null,
      page: 0,
      setPage: vi.fn(),
      totalFarms: 1,
      totalPages: 1,
    });

    mocks.useSearchProfiles.mockReturnValue({
      profile: FARM,
      isLoading: false,
      error: null,
      refetch: mocks.refetch,
      replaceProfile: mocks.replaceProfile,
    });

    mocks.useFarms.mockReturnValue({
      updateFarm: mocks.updateFarm,
    });

    mocks.useProfileActions.mockReturnValue({
      regenerateProfile: mocks.regenerateProfile,
      isRegenerating: false,
      actionError: null,
      actionMessage: null,
      clearActionFeedback: mocks.clearActionFeedback,
    });

    mocks.updateFarm.mockResolvedValue(true);
    mocks.refetch.mockResolvedValue(undefined);

    mocks.regenerateProfile.mockResolvedValue({
      id: 42,
      status: "success",
      rainfall_mm: 1500,
      temperature_celsius: 25,
      elevation_m: 300,
      ph: 7,
      slope: 5,
      soil_texture: "Sandy loam",
      area_ha: 13,
      latitude: -38,
      longitude: 145,
      coastal: false,
      riparian: true,
      nitrogen_fixing: false,
      shade_tolerant: true,
      bank_stabilising: true,
    });
  });

  it("opens and closes the existing farm edit modal", async () => {
    const user = userEvent.setup();

    renderPage();

    await user.click(screen.getByRole("button", { name: "Panel Edit" }));

    expect(
      screen.getByRole("dialog", {
        name: "Edit farm modal",
      })
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Close modal" }));

    expect(
      screen.queryByRole("dialog", {
        name: "Edit farm modal",
      })
    ).not.toBeInTheDocument();
  });

  it("updates and refreshes the searched profile after editing", async () => {
    const user = userEvent.setup();

    renderPage();

    await user.click(screen.getByRole("button", { name: "Panel Edit" }));

    await user.click(screen.getByRole("button", { name: "Save modal" }));

    await waitFor(() => {
      expect(mocks.updateFarm).toHaveBeenCalledWith(42, {
        rainfall_mm: 2000,
      });
    });

    expect(mocks.refetch).toHaveBeenCalledTimes(1);

    await waitFor(() => {
      expect(
        screen.queryByRole("dialog", {
          name: "Edit farm modal",
        })
      ).not.toBeInTheDocument();
    });

    await waitFor(() => {
      expect(mockToastSuccess).toHaveBeenCalledWith(
        "Environmental profile updated successfully"
      )
    });
  });

  it("keeps the modal open when the farm update fails", async () => {
    mocks.updateFarm.mockResolvedValue(false);

    const user = userEvent.setup();

    renderPage();

    await user.click(screen.getByRole("button", { name: "Panel Edit" }));

    await user.click(screen.getByRole("button", { name: "Save modal" }));

    await waitFor(() => {
      expect(mocks.updateFarm).toHaveBeenCalled();
    });

    expect(mocks.refetch).not.toHaveBeenCalled();

    expect(
      screen.getByRole("dialog", {
        name: "Edit farm modal",
      })
    ).toBeInTheDocument();
  });

  it("regenerates and replaces the displayed profile", async () => {
    const user = userEvent.setup();

    renderPage();

    await user.click(
      screen.getByRole("button", {
        name: "Panel Regenerate",
      })
    );

    await waitFor(() => {
      expect(mocks.regenerateProfile).toHaveBeenCalledWith(42);
    });

    expect(mocks.replaceProfile).toHaveBeenCalledWith(
      expect.objectContaining({
        id: 42,
        rainfall_mm: 1500,
        temperature_celsius: 25,
        elevation_m: 300,
        ph: 7,
        slope: 5,
        area_ha: 13,
        latitude: -38,
        longitude: 145,
        coastal: false,
        riparian: true,
        nitrogen_fixing: false,
        shade_tolerant: true,
        bank_stabilising: true,
        soil_texture: {
          name: "Sandy loam",
        },
      })
    );
  });

  it("retains existing values when regeneration omits optional values", async () => {
    mocks.regenerateProfile.mockResolvedValue({
      status: "success",
      soil_texture: "   ",
    });

    const user = userEvent.setup();

    renderPage();

    await user.click(
      screen.getByRole("button", {
        name: "Panel Regenerate",
      })
    );

    await waitFor(() => {
      expect(mocks.replaceProfile).toHaveBeenCalled();
    });

    expect(mocks.replaceProfile).toHaveBeenCalledWith(
      expect.objectContaining({
        id: FARM.id,
        rainfall_mm: FARM.rainfall_mm,
        temperature_celsius: FARM.temperature_celsius,
        elevation_m: FARM.elevation_m,
        ph: FARM.ph,
        slope: FARM.slope,
        area_ha: FARM.area_ha,
        latitude: FARM.latitude,
        longitude: FARM.longitude,
        coastal: FARM.coastal,
        riparian: FARM.riparian,
        nitrogen_fixing: FARM.nitrogen_fixing,
        shade_tolerant: FARM.shade_tolerant,
        bank_stabilising: FARM.bank_stabilising,
        soil_texture: FARM.soil_texture,
      })
    );
  });

  it("does not replace the profile when regeneration fails", async () => {
    mocks.regenerateProfile.mockRejectedValue(new Error("Regeneration failed"));

    const user = userEvent.setup();

    renderPage();

    await user.click(
      screen.getByRole("button", {
        name: "Panel Regenerate",
      })
    );

    await waitFor(() => {
      expect(mocks.regenerateProfile).toHaveBeenCalledWith(42);
    });

    expect(mocks.replaceProfile).not.toHaveBeenCalled();
  });

  it("does nothing when Edit or Regenerate is triggered without a profile", async () => {
    mocks.useSearchProfiles.mockReturnValue({
      profile: null,
      isLoading: false,
      error: null,
      refetch: mocks.refetch,
      replaceProfile: mocks.replaceProfile,
    });

    const user = userEvent.setup();

    renderPage();

    await user.click(screen.getByRole("button", { name: "Panel Edit" }));

    await user.click(
      screen.getByRole("button", {
        name: "Panel Regenerate",
      })
    );

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    expect(mocks.regenerateProfile).not.toHaveBeenCalled();

    expect(mocks.replaceProfile).not.toHaveBeenCalled();
  });

  it("clears action feedback when the page or query changes", () => {
    renderPage();

    expect(mocks.clearActionFeedback).toHaveBeenCalled();

    expect(screen.getByTestId("current-query")).toHaveTextContent("42");
  });

  it("shows the normal farm list after the search is cleared", async () => {
    const user = userEvent.setup();

    renderPage();

    expect(screen.queryByTestId("farm-list")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Clear query" }));

    expect(screen.getByTestId("farm-list")).toBeInTheDocument();
  });
});
