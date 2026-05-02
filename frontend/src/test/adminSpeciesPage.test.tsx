import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HelmetProvider } from "react-helmet-async";
import { describe, expect, it, vi, beforeEach } from "vitest";

import AdminSpeciesPage from "../pages/admin/AdminSpeciesPage";
import {
  createSpecies,
  deleteSpecies,
  getAllSpecies,
  getSoilTextures,
  updateSpecies,
} from "../utils/speciesApi";

vi.mock("../utils/speciesApi", () => ({
  getAllSpecies: vi.fn(),
  getSoilTextures: vi.fn(),
  createSpecies: vi.fn(),
  updateSpecies: vi.fn(),
  deleteSpecies: vi.fn(),
}));

vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: () => "test-token",
  }),
}));

const mockSpecies = [
  {
    id: 1,
    name: "Casuarina equisetifolia",
    common_name: "Ai-kakeu",
    rainfall_mm_min: 200,
    rainfall_mm_max: 3500,
    temperature_celsius_min: 10,
    temperature_celsius_max: 35,
    elevation_m_min: 0,
    elevation_m_max: 1400,
    ph_min: 5.0,
    ph_max: 7.7,
    coastal: true,
    riparian: false,
    nitrogen_fixing: true,
    shade_tolerant: false,
    bank_stabilising: true,
    soil_textures: [
      { id: 1, name: "sand" },
      { id: 4, name: "loam" },
    ],
    agroforestry_types: [{ id: 1, type_name: "block" }],
  },
];

const mockSoilTextures = [
  { id: 1, name: "sand" },
  { id: 4, name: "loam" },
];

function renderPage() {
  return render(
    <HelmetProvider>
      <AdminSpeciesPage />
    </HelmetProvider>
  );
}

describe("AdminSpeciesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(getAllSpecies).mockResolvedValue(mockSpecies);
    vi.mocked(getSoilTextures).mockResolvedValue(mockSoilTextures);
    vi.mocked(createSpecies).mockResolvedValue(mockSpecies[0]);
    vi.mocked(updateSpecies).mockResolvedValue(mockSpecies[0]);
    vi.mocked(deleteSpecies).mockResolvedValue(undefined);
  });

  it("loads and displays species records", async () => {
    renderPage();

    expect(screen.getByText(/loading species/i)).toBeInTheDocument();

    expect(
      await screen.findByText("Casuarina equisetifolia")
    ).toBeInTheDocument();

    expect(screen.getByText("Ai-kakeu")).toBeInTheDocument();
    expect(screen.getByText("200–3500 mm")).toBeInTheDocument();
    expect(screen.getByText("10–35°C")).toBeInTheDocument();
    expect(screen.getByText("5–7.7")).toBeInTheDocument();
    expect(screen.getByText("2 soils")).toBeInTheDocument();
    expect(screen.getByText("1 type")).toBeInTheDocument();
  });

  it("opens add species modal", async () => {
    const user = userEvent.setup();

    renderPage();

    await screen.findByText("Casuarina equisetifolia");

    await user.click(screen.getByRole("button", { name: /add species/i }));

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /add species/i })
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/scientific name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/common name/i)).toBeInTheDocument();
  });

  it("creates a species and refreshes the list", async () => {
    const user = userEvent.setup();

    renderPage();

    await screen.findByText("Casuarina equisetifolia");

    await user.click(screen.getByRole("button", { name: /add species/i }));

    await user.type(screen.getByLabelText(/scientific name/i), "Test species");
    await user.type(screen.getByLabelText(/common name/i), "Test common");

    await user.click(screen.getByLabelText("sand"));
    await user.click(screen.getByLabelText("block"));

    await user.click(screen.getByRole("button", { name: /save species/i }));

    await waitFor(() => {
      expect(createSpecies).toHaveBeenCalled();
    });

    expect(createSpecies).toHaveBeenCalledWith(
      expect.objectContaining({
        name: "Test species",
        common_name: "Test common",
        soil_textures: [1],
        agroforestry_types: [1],
      }),
      "test-token"
    );

    expect(
      await screen.findByText(/species created successfully/i)
    ).toBeInTheDocument();
  });

  it("opens edit modal with prefilled species data", async () => {
    const user = userEvent.setup();

    renderPage();

    await screen.findByText("Casuarina equisetifolia");

    await user.click(screen.getByRole("button", { name: /edit/i }));

    expect(
      screen.getByRole("heading", { name: /edit species/i })
    ).toBeInTheDocument();
    expect(
      screen.getByDisplayValue("Casuarina equisetifolia")
    ).toBeInTheDocument();
    expect(screen.getByDisplayValue("Ai-kakeu")).toBeInTheDocument();
    expect(screen.getByLabelText("sand")).toBeChecked();
    expect(screen.getByLabelText("block")).toBeChecked();
  });

  it("updates a species and refreshes the list", async () => {
    const user = userEvent.setup();

    renderPage();

    await screen.findByText("Casuarina equisetifolia");

    await user.click(screen.getByRole("button", { name: /edit/i }));

    const commonNameInput = screen.getByLabelText(/common name/i);
    await user.clear(commonNameInput);
    await user.type(commonNameInput, "Updated common");

    await user.click(screen.getByRole("button", { name: /save species/i }));

    await waitFor(() => {
      expect(updateSpecies).toHaveBeenCalled();
    });

    expect(updateSpecies).toHaveBeenCalledWith(
      1,
      expect.objectContaining({
        common_name: "Updated common",
      }),
      "test-token"
    );

    expect(
      await screen.findByText(/species updated successfully/i)
    ).toBeInTheDocument();
  });

  it("deletes a species after confirmation", async () => {
    const user = userEvent.setup();

    vi.spyOn(window, "confirm").mockReturnValue(true);

    renderPage();

    await screen.findByText("Casuarina equisetifolia");

    await user.click(screen.getByRole("button", { name: /delete/i }));

    await waitFor(() => {
      expect(deleteSpecies).toHaveBeenCalledWith(1, "test-token");
    });

    expect(
      await screen.findByText(/species deleted successfully/i)
    ).toBeInTheDocument();
  });

  it("does not delete when confirmation is cancelled", async () => {
    const user = userEvent.setup();

    vi.spyOn(window, "confirm").mockReturnValue(false);

    renderPage();

    await screen.findByText("Casuarina equisetifolia");

    await user.click(screen.getByRole("button", { name: /delete/i }));

    expect(deleteSpecies).not.toHaveBeenCalled();
  });

  it("shows an error when loading species fails", async () => {
    vi.mocked(getAllSpecies).mockRejectedValue(new Error("Failed to fetch"));

    renderPage();

    expect(await screen.findByText("Failed to fetch")).toBeInTheDocument();
  });
});

it("shows backend validation error inside the create modal and keeps it open", async () => {
  const user = userEvent.setup();

  vi.mocked(getAllSpecies).mockResolvedValue(mockSpecies);
  vi.mocked(getSoilTextures).mockResolvedValue(mockSoilTextures);
  vi.mocked(createSpecies).mockRejectedValue(
    new Error("Temperature must be less than or equal to 50.")
  );

  renderPage();

  await screen.findByRole("button", { name: /add species/i });

  await user.click(screen.getByRole("button", { name: /add species/i }));

  await user.type(screen.getByLabelText(/scientific name/i), "Invalid species");
  await user.type(screen.getByLabelText(/common name/i), "Invalid common");

  await user.click(screen.getByLabelText("sand"));
  await user.click(screen.getByLabelText("block"));

  await user.click(screen.getByRole("button", { name: /save species/i }));

  expect(
    await screen.findByText("Temperature must be less than or equal to 50.")
  ).toBeInTheDocument();

  expect(screen.getByRole("dialog")).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /add species/i })
  ).toBeInTheDocument();
  expect(
    screen.queryByText(/species created successfully/i)
  ).not.toBeInTheDocument();
});

it("clears backend validation error when the create modal is reopened", async () => {
  const user = userEvent.setup();

  vi.mocked(getAllSpecies).mockResolvedValue(mockSpecies);
  vi.mocked(getSoilTextures).mockResolvedValue(mockSoilTextures);
  vi.mocked(createSpecies).mockRejectedValueOnce(
    new Error("Temperature must be less than or equal to 50.")
  );

  renderPage();

  await screen.findByRole("button", { name: /add species/i });

  await user.click(screen.getByRole("button", { name: /add species/i }));

  await user.type(screen.getByLabelText(/scientific name/i), "Invalid species");
  await user.type(screen.getByLabelText(/common name/i), "Invalid common");

  await user.click(screen.getByLabelText("sand"));
  await user.click(screen.getByLabelText("block"));

  await user.click(screen.getByRole("button", { name: /save species/i }));

  expect(
    await screen.findByText("Temperature must be less than or equal to 50.")
  ).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: /cancel/i }));
  await user.click(screen.getByRole("button", { name: /add species/i }));

  expect(
    screen.queryByText("Temperature must be less than or equal to 50.")
  ).not.toBeInTheDocument();
});

it("shows backend validation error inside the edit modal and keeps it open", async () => {
  const user = userEvent.setup();

  vi.mocked(getAllSpecies).mockResolvedValue(mockSpecies);
  vi.mocked(getSoilTextures).mockResolvedValue(mockSoilTextures);
  vi.mocked(updateSpecies).mockRejectedValue(
    new Error("pH must be between 0 and 14.")
  );

  renderPage();

  await screen.findByRole("button", { name: /edit/i });

  await user.click(screen.getByRole("button", { name: /edit/i }));
  await user.click(screen.getByRole("button", { name: /save species/i }));

  expect(
    await screen.findByText("pH must be between 0 and 14.")
  ).toBeInTheDocument();

  expect(screen.getByRole("dialog")).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /edit species/i })
  ).toBeInTheDocument();
  expect(
    screen.queryByText(/species updated successfully/i)
  ).not.toBeInTheDocument();
});
