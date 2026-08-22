import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ExclusionRulesPage from "@/pages/admin/settings/ExclusionRulesPage";
import { getAllSpecies } from "../utils/speciesApi";

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
    ph_min: 6,
    ph_max: 8,
    coastal: false,
    riparian: false,
    nitrogen_fixing: false,
    shade_tolerant: false,
    bank_stabilising: false,
    soil_textures: [],
    agroforestry_types: [],
  },
  {
    id: 2,
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
    coastal: false,
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
        <ExclusionRulesPage />
      </HelmetProvider>
    </MemoryRouter>
  );
}

describe("ExclusionRulesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getAllSpecies).mockResolvedValue(mockSpecies);
  });

  it("loads species and displays the empty state", async () => {
    renderPage();

    expect(screen.getByText("Loading species...")).toBeInTheDocument();

    await waitFor(() => {
      expect(
        screen.getByText("No exclusion rules have been configured.")
      ).toBeInTheDocument();
    });

    expect(getAllSpecies).toHaveBeenCalledWith("test-token");
  });

  it("opens the create modal", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /add exclusion rule/i })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", { name: /add exclusion rule/i })
    );

    expect(
      screen.getByRole("heading", { name: "Add Exclusion Rule" })
    ).toBeInTheDocument();

    expect(screen.getByLabelText(/^species$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^feature$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^operator$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^value$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^reason$/i)).toBeInTheDocument();
  });

  it("creates a draft exclusion rule", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /add exclusion rule/i })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", { name: /add exclusion rule/i })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");
    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");
    await user.selectOptions(screen.getByLabelText(/^operator$/i), "<");
    await user.type(screen.getByLabelText(/^value$/i), "1000");
    await user.type(
      screen.getByLabelText(/^reason$/i),
      "Rainfall below survival threshold"
    );

    await user.click(screen.getByRole("button", { name: /add rule/i }));

    expect(screen.getByText("Tectona grandis")).toBeInTheDocument();
    expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
    expect(screen.getByText("1000")).toBeInTheDocument();
    expect(
      screen.getByText("Rainfall below survival threshold")
    ).toBeInTheDocument();
  });

  it("opens the edit modal with existing values", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /add exclusion rule/i })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", { name: /add exclusion rule/i })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");
    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");
    await user.type(screen.getByLabelText(/^value$/i), "1000");
    await user.type(screen.getByLabelText(/^reason$/i), "Too dry");

    await user.click(screen.getByRole("button", { name: /add rule/i }));

    await user.click(screen.getByRole("button", { name: /edit/i }));

    expect(
      screen.getByRole("heading", { name: "Edit Exclusion Rule" })
    ).toBeInTheDocument();

    expect(screen.getByLabelText(/^species$/i)).toHaveValue("1");
    expect(screen.getByLabelText(/^feature$/i)).toHaveValue("rainfall_mm");
    expect(screen.getByLabelText(/^value$/i)).toHaveValue("1000");
    expect(screen.getByLabelText(/^reason$/i)).toHaveValue("Too dry");
  });

  it("updates a draft exclusion rule", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /add exclusion rule/i })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", { name: /add exclusion rule/i })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");
    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");
    await user.type(screen.getByLabelText(/^value$/i), "1000");
    await user.type(screen.getByLabelText(/^reason$/i), "Too dry");

    await user.click(screen.getByRole("button", { name: /add rule/i }));
    await user.click(screen.getByRole("button", { name: /edit/i }));

    const reasonInput = screen.getByLabelText(/^reason$/i);

    await user.clear(reasonInput);
    await user.type(reasonInput, "Updated reason");

    await user.click(screen.getByRole("button", { name: /update rule/i }));

    expect(screen.getByText("Updated reason")).toBeInTheDocument();
    expect(screen.queryByText("Too dry")).not.toBeInTheDocument();
  });

  it("deletes a draft exclusion rule", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /add exclusion rule/i })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", { name: /add exclusion rule/i })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");
    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");
    await user.type(screen.getByLabelText(/^value$/i), "1000");
    await user.type(screen.getByLabelText(/^reason$/i), "Too dry");

    await user.click(screen.getByRole("button", { name: /add rule/i }));

    expect(screen.getByText("rainfall_mm")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /delete/i }));

    expect(screen.queryByText("rainfall_mm")).not.toBeInTheDocument();
  });

  it("shows validation when required values are missing", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /add exclusion rule/i })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", { name: /add exclusion rule/i })
    );

    const addButton = screen.getByRole("button", { name: /add rule/i });
    const form = addButton.closest("form");

    expect(form).not.toBeNull();

    fireEvent.submit(form!);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Please select a species."
    );
  });

  it("changes the value placeholder for set operators", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /add exclusion rule/i })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", { name: /add exclusion rule/i })
    );

    await user.selectOptions(screen.getByLabelText(/^operator$/i), "in_set");

    expect(screen.getByLabelText(/^value$/i)).toHaveAttribute(
      "placeholder",
      "e.g. clay, loam, sandy"
    );
  });

  it("closes the modal when Cancel is clicked", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /add exclusion rule/i })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", { name: /add exclusion rule/i })
    );

    await user.click(screen.getByRole("button", { name: /cancel/i }));

    expect(
      screen.queryByRole("heading", { name: "Add Exclusion Rule" })
    ).not.toBeInTheDocument();
  });

  it("validates feature, value, and reason fields", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /add exclusion rule/i })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", { name: /add exclusion rule/i })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");

    const form = screen
      .getByRole("button", { name: /add rule/i })
      .closest("form");

    expect(form).not.toBeNull();

    fireEvent.submit(form!);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Please enter a feature."
    );

    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");

    fireEvent.submit(form!);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Please enter a rule value."
    );

    await user.type(screen.getByLabelText(/^value$/i), "1000");

    fireEvent.submit(form!);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Please enter a reason for the exclusion."
    );
  });

  it("shows an error when species loading fails", async () => {
    vi.mocked(getAllSpecies).mockRejectedValue(
      new Error("Unable to load species")
    );

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Unable to load species")).toBeInTheDocument();
    });

    expect(
      screen.getByRole("button", { name: /add exclusion rule/i })
    ).toBeDisabled();
  });
});
