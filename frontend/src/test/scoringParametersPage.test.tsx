import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ScoringParametersPage from "@/pages/admin/settings/ScoringParametersPage";
import {
  createParameter,
  deleteParameter,
  getAllParameters,
  updateParameter,
} from "../utils/parametersApi";
import { getAllSpecies } from "../utils/speciesApi";

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

vi.mock("../utils/parametersApi", () => ({
  getAllParameters: vi.fn(),
  createParameter: vi.fn(),
  updateParameter: vi.fn(),
  deleteParameter: vi.fn(),
}));

vi.mock("../utils/speciesApi", () => ({
  getAllSpecies: vi.fn(),
}));

vi.mock("../contexts/AuthContext", () => {
  const getAccessToken = () => "test-token";
  return {
    useAuth: () => ({ getAccessToken }),
  };
});

const mockSpecies = [
  {
    id: 1,
    name: "Tectona grandis",
    common_name: "Teak",
    rainfall_mm_min: 1000,
    rainfall_mm_max: 2000,
    temperature_celsius_min: 20,
    temperature_celsius_max: 35,
    elevation_m_min: 0,
    elevation_m_max: 800,
    ph_min: 6.0,
    ph_max: 8.0,
    coastal: false,
    riparian: false,
    nitrogen_fixing: false,
    shade_tolerant: false,
    bank_stabilising: false,
    soil_textures: [],
    agroforestry_types: [],
  },
];

const mockParameters = [
  {
    id: 1,
    species_id: 1,
    feature: "rainfall_mm",
    score_method: "trapezoid",
    weight: 0.4,
    trap_left_tol: 100,
    trap_right_tol: 200,
  },
  {
    id: 2,
    species_id: 1,
    feature: "temperature_celsius",
    score_method: "trapezoid",
    weight: 0.3,
    trap_left_tol: null,
    trap_right_tol: null,
  },
];

function renderPage() {
  return render(
    <MemoryRouter>
      <HelmetProvider>
        <ScoringParametersPage />
      </HelmetProvider>
    </MemoryRouter>
  );
}

describe("ScoringParametersPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getAllParameters).mockResolvedValue(mockParameters);
    vi.mocked(getAllSpecies).mockResolvedValue(mockSpecies);
    mockToastSuccess.mockClear();
    mockToastError.mockClear();
  });

  it("loads and displays scoring parameters", async () => {
    renderPage();

    expect(
      screen.getByText("Loading scoring parameters...")
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    expect(screen.getByText("temperature_celsius")).toBeInTheDocument();
    expect(screen.getAllByText("Tectona grandis")).toHaveLength(2);
    expect(screen.getAllByText("trapezoid")).toHaveLength(2);
  });

  it("shows error when load fails", async () => {
    vi.mocked(getAllParameters).mockRejectedValue(new Error("Network error"));

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Network error")).toBeInTheDocument();
    });
  });

  it("opens create modal when Add Parameter is clicked", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /add parameter/i }));

    expect(screen.getByRole("dialog", { name: "" })).toBeInTheDocument();
    expect(screen.getByText("Add Scoring Parameter")).toBeInTheDocument();
  });

  it("creates a parameter successfully", async () => {
    vi.mocked(createParameter).mockResolvedValue({
      id: 3,
      species_id: 1,
      feature: "elevation",
      score_method: "trapezoid",
      weight: 0.3,
      trap_left_tol: null,
      trap_right_tol: null,
    });

    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /add parameter/i }));

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");
    await user.selectOptions(
      screen.getByLabelText(/^feature$/i),
      "elevation_m"
    );
    await user.selectOptions(
      screen.getByLabelText(/score method/i),
      "trapezoid"
    );

    await user.click(screen.getByRole("button", { name: /save parameter/i }));

    await waitFor(() => {
      expect(createParameter).toHaveBeenCalledWith(
        expect.objectContaining({
          species_id: 1,
          feature: "elevation_m",
          score_method: "trapezoid",
          weight: 0,
        }),
        "test-token"
      );
    });

    await waitFor(() => {
      expect(mockToastSuccess).toHaveBeenCalledWith(
        "Scoring parameter created successfully"
      ); 
    });
  });

  it("opens edit modal with prefilled data", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole("button", { name: /edit/i });
    await user.click(editButtons[0]);

    expect(screen.getByText("Edit Scoring Parameter")).toBeInTheDocument();

    const featureSelect = screen.getByLabelText(/^feature$/i);
    expect(featureSelect).toHaveValue("rainfall_mm");
  });

  it("updates a parameter successfully", async () => {
    vi.mocked(updateParameter).mockResolvedValue({
      ...mockParameters[0],
      feature: "rainfall_updated",
    });

    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole("button", { name: /edit/i });
    await user.click(editButtons[0]);

    await user.selectOptions(
      screen.getByLabelText(/^feature$/i),
      "elevation_m"
    );

    await user.click(screen.getByRole("button", { name: /save parameter/i }));

    await waitFor(() => {
      expect(updateParameter).toHaveBeenCalledWith(
        1,
        expect.objectContaining({ feature: "elevation_m" }),
        "test-token"
      );
      const updateCall = vi.mocked(updateParameter).mock.calls[0][1];
      expect(updateCall).not.toHaveProperty("weight");
    });

    await waitFor(() => {
      expect(mockToastSuccess).toHaveBeenCalledWith(
        "Scoring parameter updated successfully"
      );
    });
  });

  it("deletes a parameter after confirmation", async () => {
    vi.mocked(deleteParameter).mockResolvedValue(undefined);
    vi.spyOn(window, "confirm").mockReturnValue(true);

    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole("button", { name: /delete/i });
    await user.click(deleteButtons[0]);

    await waitFor(() => {
      expect(deleteParameter).toHaveBeenCalledWith(1, "test-token");
    });

    await waitFor(() => {
      expect(mockToastSuccess).toHaveBeenCalledWith(
        "Scoring parameter deleted successfully"
      );
    });
  });

  it("does not delete when confirmation is cancelled", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);

    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole("button", { name: /delete/i });
    await user.click(deleteButtons[0]);

    expect(deleteParameter).not.toHaveBeenCalled();
  });

  it("shows form error in modal and keeps modal open", async () => {
    vi.mocked(createParameter).mockRejectedValue(
      new Error("Species not found")
    );

    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /add parameter/i }));

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");
    await user.selectOptions(
      screen.getByLabelText(/^feature$/i),
      "elevation_m"
    );
    await user.selectOptions(
      screen.getByLabelText(/score method/i),
      "trapezoid"
    );

    await user.click(screen.getByRole("button", { name: /save parameter/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Species not found");
    });

    expect(screen.getByText("Add Scoring Parameter")).toBeInTheDocument();
  });

  it("closes modal when Cancel is clicked", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /add parameter/i }));
    expect(screen.getByText("Add Scoring Parameter")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /cancel/i }));
    expect(screen.queryByText("Add Scoring Parameter")).not.toBeInTheDocument();
  });

  it("shows empty state when no parameters exist", async () => {
    vi.mocked(getAllParameters).mockResolvedValue([]);

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByText("No scoring parameters found.")
      ).toBeInTheDocument();
    });
  });

  it("shows tolerance fields only when score method is trapezoid", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /add parameter/i }));

    expect(
      screen.queryByLabelText(/trap left tolerance/i)
    ).not.toBeInTheDocument();
    expect(
      screen.queryByLabelText(/trap right tolerance/i)
    ).not.toBeInTheDocument();

    await user.selectOptions(
      screen.getByLabelText(/score method/i),
      "trapezoid"
    );

    expect(screen.getByLabelText(/trap left tolerance/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/trap right tolerance/i)).toBeInTheDocument();

    await user.selectOptions(
      screen.getByLabelText(/score method/i),
      "num_range"
    );

    expect(
      screen.queryByLabelText(/trap left tolerance/i)
    ).not.toBeInTheDocument();
    expect(
      screen.queryByLabelText(/trap right tolerance/i)
    ).not.toBeInTheDocument();
  });

  it("shows error when delete fails", async () => {
    vi.mocked(deleteParameter).mockRejectedValue(new Error("Delete failed"));
    vi.spyOn(window, "confirm").mockReturnValue(true);

    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole("button", { name: /delete/i });
    await user.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith("Delete failed");
    });
  });

  it("shows validation error when no species is selected", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /add parameter/i }));

    await user.selectOptions(
      screen.getByLabelText(/^feature$/i),
      "elevation_m"
    );
    await user.selectOptions(
      screen.getByLabelText(/score method/i),
      "num_range"
    );

    await user.click(screen.getByRole("button", { name: /save parameter/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Please select a species."
      );
    });
  });

  it("clears tolerance values to null when inputs are cleared", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /add parameter/i }));
    await user.selectOptions(
      screen.getByLabelText(/score method/i),
      "trapezoid"
    );

    const trapLeft = screen.getByLabelText(/trap left tolerance/i);
    const trapRight = screen.getByLabelText(/trap right tolerance/i);

    await user.type(trapLeft, "100");
    await user.type(trapRight, "200");

    expect(trapLeft).toHaveValue(100);
    expect(trapRight).toHaveValue(200);

    await user.clear(trapLeft);
    await user.clear(trapRight);

    expect(trapLeft).toHaveValue(null);
    expect(trapRight).toHaveValue(null);
  });

  it("displays dash for null weight in the table", async () => {
    vi.mocked(getAllParameters).mockResolvedValue([
      { ...mockParameters[0], weight: null },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    });

    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("shows fallback name when species is not found", async () => {
    vi.mocked(getAllParameters).mockResolvedValue([
      { ...mockParameters[0], species_id: 999 },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Species 999")).toBeInTheDocument();
    });
  });
});
