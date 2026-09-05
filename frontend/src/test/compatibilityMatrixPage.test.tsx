import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import CompatibilityMatrixPage from "@/pages/admin/settings/CompatibilityMatrixPage";
import { getAllSpecies } from "../utils/speciesApi";

vi.mock("../utils/speciesApi", () => ({
  getAllSpecies: vi.fn(),
}));

const authState = vi.hoisted(() => {
  const state = {
    accessToken: "test-token" as string | null,
  };

  const getAccessToken = vi.fn(() => state.accessToken);

  return {
    state,
    getAccessToken,
  };
});

vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: authState.getAccessToken,
  }),
}));

const mockSpecies = [
  {
    id: 2,
    name: "Tectona grandis",
    common_name: "Teak",
    rainfall_mm_min: 1000,
    rainfall_mm_max: 2000,
    temperature_celsius_min: 20,
    temperature_celsius_max: 35,
    elevation_m_min: 0,
    elevation_m_max: 800,
    ph_min: 6,
    ph_max: 8,
    coastal: false,
    riparian: true,
    nitrogen_fixing: false,
    shade_tolerant: false,
    bank_stabilising: true,
    soil_textures: [],
    agroforestry_types: [],
  },
  {
    id: 1,
    name: "Acacia mangium",
    common_name: "Mangium",
    rainfall_mm_min: 1000,
    rainfall_mm_max: 4500,
    temperature_celsius_min: 12,
    temperature_celsius_max: 34,
    elevation_m_min: 0,
    elevation_m_max: 800,
    ph_min: 4,
    ph_max: 7,
    coastal: true,
    riparian: false,
    nitrogen_fixing: true,
    shade_tolerant: false,
    bank_stabilising: false,
    soil_textures: [],
    agroforestry_types: [],
  },
];

function renderPage() {
  return render(
    <MemoryRouter>
      <HelmetProvider>
        <CompatibilityMatrixPage />
      </HelmetProvider>
    </MemoryRouter>
  );
}

describe("CompatibilityMatrixPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    authState.state.accessToken = "test-token";

    vi.mocked(getAllSpecies).mockResolvedValue(mockSpecies);
  });

  it("loads species and displays the compatibility matrix", async () => {
    renderPage();

    expect(
      screen.getByText("Loading compatibility matrix...")
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Acacia mangium")).toBeInTheDocument();
    });

    expect(getAllSpecies).toHaveBeenCalledWith("test-token");

    expect(screen.getByText("Tectona grandis")).toBeInTheDocument();

    expect(
      screen.getByRole("columnheader", { name: "Coastal" })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("columnheader", { name: "Riparian" })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("columnheader", { name: "Nitrogen Fixing" })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("columnheader", { name: "Shade Tolerant" })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("columnheader", { name: "Bank Stabilising" })
    ).toBeInTheDocument();
  });

  it("sorts species alphabetically", async () => {
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Acacia mangium")).toBeInTheDocument();
    });

    const rows = screen.getAllByRole("row");

    expect(rows[1]).toHaveTextContent("Acacia mangium");
    expect(rows[2]).toHaveTextContent("Tectona grandis");
  });

  it("shows existing compatibility values from species data", async () => {
    renderPage();

    const coastalCheckbox = await screen.findByRole("checkbox", {
      name: "Acacia mangium Coastal",
    });

    const nitrogenCheckbox = screen.getByRole("checkbox", {
      name: "Acacia mangium Nitrogen Fixing",
    });

    const riparianCheckbox = screen.getByRole("checkbox", {
      name: "Acacia mangium Riparian",
    });

    expect(coastalCheckbox).toBeChecked();
    expect(nitrogenCheckbox).toBeChecked();
    expect(riparianCheckbox).not.toBeChecked();
  });

  it("allows a compatibility value to be toggled locally", async () => {
    const user = userEvent.setup();

    renderPage();

    const checkbox = await screen.findByRole("checkbox", {
      name: "Acacia mangium Coastal",
    });

    expect(checkbox).toBeChecked();

    await user.click(checkbox);

    expect(checkbox).not.toBeChecked();

    await user.click(checkbox);

    expect(checkbox).toBeChecked();
  });

  it("allows an initially unchecked compatibility value to be enabled", async () => {
    const user = userEvent.setup();

    renderPage();

    const checkbox = await screen.findByRole("checkbox", {
      name: "Tectona grandis Coastal",
    });

    expect(checkbox).not.toBeChecked();

    await user.click(checkbox);

    expect(checkbox).toBeChecked();
  });

  it("shows an authentication error when no access token exists", async () => {
    authState.state.accessToken = null;

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByText(
          "You must be logged in as admin to view the compatibility matrix."
        )
      ).toBeInTheDocument();
    });

    expect(getAllSpecies).not.toHaveBeenCalled();
  });

  it("shows the API error when species loading fails", async () => {
    vi.mocked(getAllSpecies).mockRejectedValue(
      new Error("Unable to load species")
    );

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Unable to load species")).toBeInTheDocument();
    });
  });

  it("shows a fallback error for a non-Error API rejection", async () => {
    vi.mocked(getAllSpecies).mockRejectedValue("request failed");

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByText("Failed to load compatibility matrix.")
      ).toBeInTheDocument();
    });
  });
});
