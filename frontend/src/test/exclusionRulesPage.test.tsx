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

import ExclusionRulesPage from "@/pages/admin/settings/ExclusionRulesPage";
import {
  createExclusionRule,
  deleteExclusionRule,
  getAllExclusionRules,
  updateExclusionRule,
} from "../utils/exclusionRulesApi";
import { getSpeciesDropdown } from "../utils/speciesApi";

vi.mock("../utils/exclusionRulesApi", () => ({
  getAllExclusionRules: vi.fn(),
  createExclusionRule: vi.fn(),
  updateExclusionRule: vi.fn(),
  deleteExclusionRule: vi.fn(),
}));

vi.mock("../utils/speciesApi", () => ({
  getSpeciesDropdown: vi.fn(),
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

const mockRule = {
  id: 10,
  species_id: 1,
  feature: "rainfall_mm",
  operator: "<" as const,
  value: 1000,
  reason: "Rainfall below survival threshold",
};

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
    authState.state.accessToken = "test-token";

    vi.mocked(getSpeciesDropdown).mockResolvedValue(mockSpecies);
    vi.mocked(getAllExclusionRules).mockResolvedValue([]);
    vi.mocked(deleteExclusionRule).mockResolvedValue();
  });

  it("loads species and exclusion rules from the API", async () => {
    vi.mocked(getAllExclusionRules).mockResolvedValue([mockRule]);

    renderPage();

    expect(screen.getByText("Loading exclusion rules...")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Tectona grandis")).toBeInTheDocument();
    });

    expect(getSpeciesDropdown).toHaveBeenCalledWith("test-token");

    expect(getAllExclusionRules).toHaveBeenCalledWith("test-token");

    expect(screen.getByText("rainfall_mm")).toBeInTheDocument();

    expect(screen.getByText("1000")).toBeInTheDocument();
  });

  it("shows the empty state when no rules exist", async () => {
    renderPage();

    await waitFor(() => {
      expect(
        screen.getByText("No exclusion rules have been configured.")
      ).toBeInTheDocument();
    });
  });

  it("opens the create modal", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    expect(
      screen.getByRole("heading", {
        name: "Add Exclusion Rule",
      })
    ).toBeInTheDocument();

    expect(screen.getByLabelText(/^species$/i)).toBeInTheDocument();

    expect(screen.getByLabelText(/^feature$/i)).toBeInTheDocument();

    expect(screen.getByLabelText(/^operator$/i)).toBeInTheDocument();

    expect(screen.getByLabelText(/^value$/i)).toBeInTheDocument();

    expect(screen.getByLabelText(/^reason$/i)).toBeInTheDocument();
  });

  it("creates an exclusion rule through the API", async () => {
    const user = userEvent.setup();

    vi.mocked(createExclusionRule).mockResolvedValue(mockRule);

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");

    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");

    await user.selectOptions(screen.getByLabelText(/^operator$/i), "<");

    await user.type(screen.getByLabelText(/^value$/i), "1000");

    await user.type(
      screen.getByLabelText(/^reason$/i),
      "Rainfall below survival threshold"
    );

    await user.click(
      screen.getByRole("button", {
        name: /add rule/i,
      })
    );

    await waitFor(() => {
      expect(createExclusionRule).toHaveBeenCalledWith(
        {
          species_id: 1,
          feature: "rainfall_mm",
          operator: "<",
          value: 1000,
          reason: "Rainfall below survival threshold",
        },
        "test-token"
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Tectona grandis")).toBeInTheDocument();
    });
  });

  it("converts set values to arrays before creating a rule", async () => {
    const user = userEvent.setup();

    const setRule = {
      ...mockRule,
      operator: "in_set" as const,
      value: ["clay", "loam", "sandy"],
    };

    vi.mocked(createExclusionRule).mockResolvedValue(setRule);

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");

    await user.type(screen.getByLabelText(/^feature$/i), "soil_texture");

    await user.selectOptions(screen.getByLabelText(/^operator$/i), "in_set");

    await user.type(screen.getByLabelText(/^value$/i), "clay, loam, sandy");

    await user.type(
      screen.getByLabelText(/^reason$/i),
      "Unsupported soil texture"
    );

    await user.click(
      screen.getByRole("button", {
        name: /add rule/i,
      })
    );

    await waitFor(() => {
      expect(createExclusionRule).toHaveBeenCalledWith(
        expect.objectContaining({
          operator: "in_set",
          value: ["clay", "loam", "sandy"],
        }),
        "test-token"
      );
    });
  });

  it("opens an existing rule for editing", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllExclusionRules).mockResolvedValue([
      {
        ...mockRule,
        operator: "in_set",
        value: ["clay", "loam"],
      },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /edit/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /edit/i }));

    expect(
      screen.getByRole("heading", {
        name: "Edit Exclusion Rule",
      })
    ).toBeInTheDocument();

    expect(screen.getByLabelText(/^species$/i)).toHaveValue("1");

    expect(screen.getByLabelText(/^feature$/i)).toHaveValue("rainfall_mm");

    expect(screen.getByLabelText(/^value$/i)).toHaveValue("clay, loam");
  });

  it("updates an exclusion rule through the API", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllExclusionRules).mockResolvedValue([mockRule]);

    const updatedRule = {
      ...mockRule,
      value: 1200,
      reason: "Updated threshold",
    };

    vi.mocked(updateExclusionRule).mockResolvedValue(updatedRule);

    renderPage();

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /edit/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /edit/i }));

    const valueInput = screen.getByLabelText(/^value$/i);

    const reasonInput = screen.getByLabelText(/^reason$/i);

    await user.clear(valueInput);
    await user.type(valueInput, "1200");

    await user.clear(reasonInput);
    await user.type(reasonInput, "Updated threshold");

    await user.click(
      screen.getByRole("button", {
        name: /update rule/i,
      })
    );

    await waitFor(() => {
      expect(updateExclusionRule).toHaveBeenCalledWith(
        10,
        {
          species_id: 1,
          feature: "rainfall_mm",
          operator: "<",
          value: 1200,
          reason: "Updated threshold",
        },
        "test-token"
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Updated threshold")).toBeInTheDocument();
    });
  });

  it("deletes an exclusion rule through the API", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllExclusionRules).mockResolvedValue([mockRule]);

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /delete/i })
      ).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /delete/i }));

    await waitFor(() => {
      expect(deleteExclusionRule).toHaveBeenCalledWith(10, "test-token");
    });

    await waitFor(() => {
      expect(screen.queryByText("rainfall_mm")).not.toBeInTheDocument();
    });

    expect(
      screen.getByText("No exclusion rules have been configured.")
    ).toBeInTheDocument();
  });

  it("shows validation for incomplete form data", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    const addButton = screen.getByRole("button", {
      name: /add rule/i,
    });

    const form = addButton.closest("form");

    expect(form).not.toBeNull();

    fireEvent.submit(form!);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Please select a species."
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");

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

  it("shows an API error when creating a rule fails", async () => {
    const user = userEvent.setup();

    vi.mocked(createExclusionRule).mockRejectedValue(
      new Error("Species does not exist.")
    );

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");

    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");

    await user.type(screen.getByLabelText(/^value$/i), "1000");

    await user.type(screen.getByLabelText(/^reason$/i), "Test reason");

    await user.click(
      screen.getByRole("button", {
        name: /add rule/i,
      })
    );

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Species does not exist."
      );
    });
  });

  it("shows an error when initial API loading fails", async () => {
    vi.mocked(getAllExclusionRules).mockRejectedValue(
      new Error("Unable to load exclusion rules")
    );

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByText("Unable to load exclusion rules")
      ).toBeInTheDocument();
    });

    expect(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    ).toBeDisabled();
  });

  it("shows an error when deleting a rule fails", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllExclusionRules).mockResolvedValue([mockRule]);

    vi.mocked(deleteExclusionRule).mockRejectedValue(
      new Error("Unable to delete rule")
    );

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /delete/i })
      ).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /delete/i }));

    await waitFor(() => {
      expect(screen.getByText("Unable to delete rule")).toBeInTheDocument();
    });

    expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
  });

  it("shows the species id when the species is missing from the dropdown", async () => {
    vi.mocked(getAllExclusionRules).mockResolvedValue([
      {
        ...mockRule,
        species_id: 999,
      },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Species 999")).toBeInTheDocument();
    });
  });

  it("shows Saving and disables the form while creating a rule", async () => {
    const user = userEvent.setup();

    let resolveCreate: ((value: typeof mockRule) => void) | undefined;

    vi.mocked(createExclusionRule).mockImplementation(
      () =>
        new Promise(resolve => {
          resolveCreate = resolve;
        })
    );

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");

    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");

    await user.type(screen.getByLabelText(/^value$/i), "1000");

    await user.type(
      screen.getByLabelText(/^reason$/i),
      "Rainfall below survival threshold"
    );

    await user.click(screen.getByRole("button", { name: /add rule/i }));

    expect(screen.getByRole("button", { name: /saving/i })).toBeDisabled();

    expect(screen.getByLabelText(/^species$/i)).toBeDisabled();

    expect(screen.getByLabelText(/^feature$/i)).toBeDisabled();

    expect(screen.getByRole("button", { name: /cancel/i })).toBeDisabled();

    expect(createExclusionRule).toHaveBeenCalledTimes(1);

    const form = screen
      .getByRole("button", { name: /saving/i })
      .closest("form");

    expect(form).not.toBeNull();

    fireEvent.submit(form!);

    expect(createExclusionRule).toHaveBeenCalledTimes(1);

    await act(async () => {
      resolveCreate?.(mockRule);
    });

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(
        "Exclusion rule created successfully."
      );
    });
  });

  it("shows a success toast after updating a rule", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllExclusionRules).mockResolvedValue([mockRule]);

    vi.mocked(updateExclusionRule).mockResolvedValue({
      ...mockRule,
      reason: "Updated threshold",
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /edit/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /edit/i }));

    const reasonInput = screen.getByLabelText(/^reason$/i);

    await user.clear(reasonInput);
    await user.type(reasonInput, "Updated threshold");

    await user.click(
      screen.getByRole("button", {
        name: /update rule/i,
      })
    );

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(
        "Exclusion rule updated successfully."
      );
    });
  });

  it("shows Deleting and a success toast while deleting a rule", async () => {
    const user = userEvent.setup();

    let resolveDelete: (() => void) | undefined;

    vi.mocked(getAllExclusionRules).mockResolvedValue([mockRule]);

    vi.mocked(deleteExclusionRule).mockImplementation(
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
        "Exclusion rule deleted successfully."
      );
    });
  });

  it("keeps the modal open and shows an error toast when saving fails", async () => {
    const user = userEvent.setup();

    vi.mocked(createExclusionRule).mockRejectedValue(
      new Error("Unable to save exclusion rule")
    );

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");

    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");

    await user.type(screen.getByLabelText(/^value$/i), "1000");

    await user.type(screen.getByLabelText(/^reason$/i), "Test reason");

    await user.click(screen.getByRole("button", { name: /add rule/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Unable to save exclusion rule"
      );
    });

    expect(
      screen.getByRole("heading", {
        name: "Add Exclusion Rule",
      })
    ).toBeInTheDocument();

    expect(screen.getByRole("button", { name: /add rule/i })).toBeEnabled();
  });

  it("closes the modal when Cancel is clicked", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    await user.click(screen.getByRole("button", { name: /cancel/i }));

    expect(
      screen.queryByRole("heading", {
        name: "Add Exclusion Rule",
      })
    ).not.toBeInTheDocument();
  });

  it("dismisses a success toast from the rules page", async () => {
    const user = userEvent.setup();

    vi.mocked(createExclusionRule).mockResolvedValue(mockRule);

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");
    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");
    await user.type(screen.getByLabelText(/^value$/i), "1000");
    await user.type(screen.getByLabelText(/^reason$/i), "Test reason");

    await user.click(screen.getByRole("button", { name: /add rule/i }));

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(
        "Exclusion rule created successfully."
      );
    });

    await user.click(
      screen.getByRole("button", {
        name: /dismiss notification/i,
      })
    );

    await waitFor(() => {
      expect(screen.queryByRole("status")).not.toBeInTheDocument();
    });
  });

  it("shows an authentication toast when the token disappears before saving", async () => {
    const user = userEvent.setup();

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");
    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");
    await user.type(screen.getByLabelText(/^value$/i), "1000");
    await user.type(screen.getByLabelText(/^reason$/i), "Test reason");

    authState.state.accessToken = null;

    await user.click(screen.getByRole("button", { name: /add rule/i }));

    expect(screen.getByRole("alert")).toHaveTextContent(
      "You must be logged in as admin to save exclusion rules."
    );
    expect(createExclusionRule).not.toHaveBeenCalled();
  });

  it("shows the fallback save error for a non-Error rejection", async () => {
    const user = userEvent.setup();

    vi.mocked(createExclusionRule).mockRejectedValue("save failed");

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /add exclusion rule/i,
        })
      ).toBeEnabled();
    });

    await user.click(
      screen.getByRole("button", {
        name: /add exclusion rule/i,
      })
    );

    await user.selectOptions(screen.getByLabelText(/^species$/i), "1");
    await user.type(screen.getByLabelText(/^feature$/i), "rainfall_mm");
    await user.type(screen.getByLabelText(/^value$/i), "1000");
    await user.type(screen.getByLabelText(/^reason$/i), "Test reason");

    await user.click(screen.getByRole("button", { name: /add rule/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Failed to save exclusion rule."
      );
    });
  });

  it("shows an authentication toast when deleting without a token", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllExclusionRules).mockResolvedValue([mockRule]);

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /delete/i })
      ).toBeInTheDocument();
    });

    authState.state.accessToken = null;

    await user.click(screen.getByRole("button", { name: /delete/i }));

    expect(screen.getByRole("alert")).toHaveTextContent(
      "You must be logged in as admin to delete exclusion rules."
    );
    expect(deleteExclusionRule).not.toHaveBeenCalled();
  });

  it("shows the fallback delete error for a non-Error rejection", async () => {
    const user = userEvent.setup();

    vi.mocked(getAllExclusionRules).mockResolvedValue([mockRule]);
    vi.mocked(deleteExclusionRule).mockRejectedValue("delete failed");

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /delete/i })
      ).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /delete/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Failed to delete exclusion rule."
      );
    });

    expect(screen.getByText("rainfall_mm")).toBeInTheDocument();
  });
});
