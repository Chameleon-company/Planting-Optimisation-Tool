import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DependencyRulesPage from "@/pages/admin/settings/DependencyRulesPage";
import {
  createDependency,
  deleteDependency,
  getAllDependencies,
  updateDependency,
} from "../utils/exclusionRulesApi";
import { getSpeciesDropdown } from "../utils/speciesApi";

vi.mock("../utils/exclusionRulesApi", () => ({
  getAllDependencies: vi.fn(),
  createDependency: vi.fn(),
  updateDependency: vi.fn(),
  deleteDependency: vi.fn(),
}));

vi.mock("../utils/speciesApi", () => ({
  getSpeciesDropdown: vi.fn(),
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

const mockDependency = {
  id: 20,
  focal_species_id: 1,
  required_partner_id: 2,
};

function renderPage() {
  return render(
    <MemoryRouter>
      <HelmetProvider>
        <DependencyRulesPage />
      </HelmetProvider>
    </MemoryRouter>
  );
}

describe("DependencyRulesPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.clearAllMocks();

    vi.mocked(getSpeciesDropdown).mockResolvedValue(mockSpecies);
    vi.mocked(getAllDependencies).mockResolvedValue([]);
    vi.mocked(deleteDependency).mockResolvedValue();
  });

  it("loads species and dependencies from the API", async () => {
    vi.mocked(getAllDependencies).mockResolvedValue([mockDependency]);

    renderPage();

    expect(screen.getByText("Loading dependency rules...")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Tectona grandis")).toBeInTheDocument();
    });

    expect(getSpeciesDropdown).toHaveBeenCalledWith("test-token");

    expect(getAllDependencies).toHaveBeenCalledWith("test-token");

    expect(screen.getByText("Acacia mangium")).toBeInTheDocument();
  });

  it("shows the empty state when no dependencies exist", async () => {
    renderPage();

    await waitFor(() => {
      expect(
        screen.getByText("No dependency rules have been configured.")
      ).toBeInTheDocument();
    });
  });

  it("opens the create modal", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add dependency rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    );

    expect(
      screen.getByRole("heading", {
        name: "Add Dependency Rule",
      })
    ).toBeInTheDocument();

    expect(screen.getByLabelText(/^focal species$/i)).toBeInTheDocument();

    expect(
      screen.getByLabelText(/^required partner species$/i)
    ).toBeInTheDocument();
  });

  it("creates a dependency through the API", async () => {
    const user = userEvent.setup();

    vi.mocked(createDependency).mockResolvedValue(mockDependency);

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add dependency rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^focal species$/i), "1");

    await user.selectOptions(
      screen.getByLabelText(/^required partner species$/i),
      "2"
    );

    await user.click(
      screen.getByRole("button", {
        name: /add dependency$/i,
      })
    );

    await waitFor(() => {
      expect(createDependency).toHaveBeenCalledWith(
        {
          focal_species_id: 1,
          required_partner_id: 2,
        },
        "test-token"
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Tectona grandis")).toBeInTheDocument();
      expect(screen.getByText("Acacia mangium")).toBeInTheDocument();
    });
  });

  it("disables the focal species as a partner option", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add dependency rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^focal species$/i), "1");

    const partnerSelect = screen.getByLabelText(/^required partner species$/i);

    const focalOption = partnerSelect.querySelector('option[value="1"]');

    expect(focalOption).toBeDisabled();
  });

  it("opens an existing dependency for editing", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllDependencies).mockResolvedValue([mockDependency]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /edit/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /edit/i }));

    expect(
      screen.getByRole("heading", {
        name: "Edit Dependency Rule",
      })
    ).toBeInTheDocument();

    expect(screen.getByLabelText(/^focal species$/i)).toHaveValue("1");

    expect(screen.getByLabelText(/^required partner species$/i)).toHaveValue(
      "2"
    );
  });

  it("updates a dependency through the API", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllDependencies).mockResolvedValue([mockDependency]);

    const updatedDependency = {
      id: 20,
      focal_species_id: 2,
      required_partner_id: 1,
    };

    vi.mocked(updateDependency).mockResolvedValue(updatedDependency);

    renderPage();

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /edit/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /edit/i }));

    await user.selectOptions(screen.getByLabelText(/^focal species$/i), "2");

    await user.selectOptions(
      screen.getByLabelText(/^required partner species$/i),
      "1"
    );

    await user.click(
      screen.getByRole("button", {
        name: /update dependency/i,
      })
    );

    await waitFor(() => {
      expect(updateDependency).toHaveBeenCalledWith(
        20,
        {
          focal_species_id: 2,
          required_partner_id: 1,
        },
        "test-token"
      );
    });

    await waitFor(() => {
      const rows = screen.getAllByRole("row");

      expect(rows).toHaveLength(2);
      expect(rows[1]).toHaveTextContent("Acacia mangium");
      expect(rows[1]).toHaveTextContent("Tectona grandis");
    });
  });

  it("does not delete when confirmation is cancelled", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllDependencies).mockResolvedValue([mockDependency]);

    vi.spyOn(window, "confirm").mockReturnValue(false);

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /delete/i })
      ).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /delete/i }));

    expect(deleteDependency).not.toHaveBeenCalled();

    expect(screen.getByText("Tectona grandis")).toBeInTheDocument();
  });

  it("deletes a dependency through the API when confirmed", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllDependencies).mockResolvedValue([mockDependency]);

    vi.spyOn(window, "confirm").mockReturnValue(true);

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /delete/i })
      ).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /delete/i }));

    await waitFor(() => {
      expect(deleteDependency).toHaveBeenCalledWith(20, "test-token");
    });

    await waitFor(() => {
      expect(screen.queryByText("Tectona grandis")).not.toBeInTheDocument();
    });

    expect(
      screen.getByText("No dependency rules have been configured.")
    ).toBeInTheDocument();
  });

  it("shows validation for incomplete form data", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add dependency rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    );

    const addButton = screen.getByRole("button", {
      name: /add dependency$/i,
    });

    const form = addButton.closest("form");

    expect(form).not.toBeNull();

    fireEvent.submit(form!);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Please select a focal species."
    );

    await user.selectOptions(screen.getByLabelText(/^focal species$/i), "1");

    fireEvent.submit(form!);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Please select a required partner species."
    );
  });

  it("rejects a self dependency before calling the API", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add dependency rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    );

    const focalSelect = screen.getByLabelText(/^focal species$/i);

    const partnerSelect = screen.getByLabelText(/^required partner species$/i);

    fireEvent.change(focalSelect, {
      target: { value: "1" },
    });

    fireEvent.change(partnerSelect, {
      target: { value: "1" },
    });

    const form = screen
      .getByRole("button", {
        name: /add dependency$/i,
      })
      .closest("form");

    expect(form).not.toBeNull();

    fireEvent.submit(form!);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "A species cannot depend on itself."
    );

    expect(createDependency).not.toHaveBeenCalled();
  });

  it("shows an API error when creating a dependency fails", async () => {
    const user = userEvent.setup();

    vi.mocked(createDependency).mockRejectedValue(
      new Error("Required partner species does not exist.")
    );

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add dependency rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^focal species$/i), "1");

    await user.selectOptions(
      screen.getByLabelText(/^required partner species$/i),
      "2"
    );

    await user.click(
      screen.getByRole("button", {
        name: /add dependency$/i,
      })
    );

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Required partner species does not exist."
      );
    });
  });

  it("shows an error when initial API loading fails", async () => {
    vi.mocked(getAllDependencies).mockRejectedValue(
      new Error("Unable to load dependencies")
    );

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByText("Unable to load dependencies")
      ).toBeInTheDocument();
    });

    expect(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    ).toBeDisabled();
  });

  it("shows species ids when dependency species are missing from the dropdown", async () => {
    vi.mocked(getAllDependencies).mockResolvedValue([
      {
        id: 20,
        focal_species_id: 998,
        required_partner_id: 999,
      },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Species 998")).toBeInTheDocument();
      expect(screen.getByText("Species 999")).toBeInTheDocument();
    });
  });

  it("shows an error when deleting a dependency fails", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllDependencies).mockResolvedValue([mockDependency]);

    vi.mocked(deleteDependency).mockRejectedValue(
      new Error("Unable to delete dependency")
    );

    vi.spyOn(window, "confirm").mockReturnValue(true);

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /delete/i })
      ).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /delete/i }));

    await waitFor(() => {
      expect(
        screen.getByText("Unable to delete dependency")
      ).toBeInTheDocument();
    });

    expect(screen.getByText("Tectona grandis")).toBeInTheDocument();
  });

  it("closes the modal when Cancel is clicked", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add dependency rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    );

    await user.click(screen.getByRole("button", { name: /cancel/i }));

    expect(
      screen.queryByRole("heading", {
        name: "Add Dependency Rule",
      })
    ).not.toBeInTheDocument();
  });

  it("shows Saving and disables the form while creating a dependency", async () => {
    const user = userEvent.setup();

    let resolveCreate: ((value: typeof mockDependency) => void) | undefined;

    vi.mocked(createDependency).mockImplementation(
      () =>
        new Promise(resolve => {
          resolveCreate = resolve;
        })
    );

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add dependency rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^focal species$/i), "1");

    await user.selectOptions(
      screen.getByLabelText(/^required partner species$/i),
      "2"
    );

    await user.click(
      screen.getByRole("button", {
        name: /add dependency$/i,
      })
    );

    expect(screen.getByRole("button", { name: /saving/i })).toBeDisabled();

    expect(screen.getByLabelText(/^focal species$/i)).toBeDisabled();

    expect(screen.getByLabelText(/^required partner species$/i)).toBeDisabled();

    expect(screen.getByRole("button", { name: /cancel/i })).toBeDisabled();

    expect(createDependency).toHaveBeenCalledTimes(1);

    await act(async () => {
      resolveCreate?.(mockDependency);
    });

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(
        "Dependency rule created successfully."
      );
    });
  });

  it("shows a success toast after updating a dependency", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllDependencies).mockResolvedValue([mockDependency]);

    vi.mocked(updateDependency).mockResolvedValue({
      id: 20,
      focal_species_id: 2,
      required_partner_id: 1,
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /edit/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /edit/i }));

    await user.selectOptions(screen.getByLabelText(/^focal species$/i), "2");

    await user.selectOptions(
      screen.getByLabelText(/^required partner species$/i),
      "1"
    );

    await user.click(
      screen.getByRole("button", {
        name: /update dependency/i,
      })
    );

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(
        "Dependency rule updated successfully."
      );
    });
  });

  it("shows Deleting and a success toast while deleting a dependency", async () => {
    const user = userEvent.setup();

    let resolveDelete: (() => void) | undefined;

    vi.mocked(getAllDependencies).mockResolvedValue([mockDependency]);

    vi.spyOn(window, "confirm").mockReturnValue(true);

    vi.mocked(deleteDependency).mockImplementation(
      () =>
        new Promise(resolve => {
          resolveDelete = resolve;
        })
    );

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /delete/i })
      ).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /delete/i }));

    expect(screen.getByRole("button", { name: /deleting/i })).toBeDisabled();

    expect(screen.getByRole("button", { name: /edit/i })).toBeDisabled();

    await act(async () => {
      resolveDelete?.();
    });

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(
        "Dependency rule deleted successfully."
      );
    });
  });

  it("keeps the modal open and shows an error toast when saving fails", async () => {
    const user = userEvent.setup();

    vi.mocked(createDependency).mockRejectedValue(
      new Error("Unable to save dependency rule")
    );

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add dependency rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^focal species$/i), "1");

    await user.selectOptions(
      screen.getByLabelText(/^required partner species$/i),
      "2"
    );

    await user.click(
      screen.getByRole("button", {
        name: /add dependency$/i,
      })
    );

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Unable to save dependency rule"
      );
    });

    expect(
      screen.getByRole("heading", {
        name: "Add Dependency Rule",
      })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: /add dependency$/i,
      })
    ).toBeEnabled();
  });
});
