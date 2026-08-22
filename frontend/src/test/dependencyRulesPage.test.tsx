import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DependencyRulesPage from "@/pages/admin/settings/DependencyRulesPage";
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
        <DependencyRulesPage />
      </HelmetProvider>
    </MemoryRouter>
  );
}

describe("DependencyRulesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getAllSpecies).mockResolvedValue(mockSpecies);
  });

  it("loads species and displays the empty state", async () => {
    renderPage();

    expect(screen.getByText("Loading species...")).toBeInTheDocument();

    await waitFor(() => {
      expect(
        screen.getByText("No dependency rules have been configured.")
      ).toBeInTheDocument();
    });

    expect(getAllSpecies).toHaveBeenCalledWith("test-token");
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

  it("creates a draft dependency rule", async () => {
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

    await user.selectOptions(
      screen.getByLabelText(/^required partner species$/i),
      "2"
    );

    await user.click(
      screen.getByRole("button", {
        name: /add dependency$/i,
      })
    );

    expect(screen.getByText("Tectona grandis")).toBeInTheDocument();

    expect(screen.getByText("Acacia mangium")).toBeInTheDocument();
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

  it("opens the edit modal with existing values", async () => {
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

    await user.selectOptions(
      screen.getByLabelText(/^required partner species$/i),
      "2"
    );

    await user.click(
      screen.getByRole("button", {
        name: /add dependency$/i,
      })
    );

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

  it("updates a draft dependency rule", async () => {
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

    await user.selectOptions(
      screen.getByLabelText(/^required partner species$/i),
      "2"
    );

    await user.click(
      screen.getByRole("button", {
        name: /add dependency$/i,
      })
    );

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

    const rows = screen.getAllByRole("row");

    expect(rows).toHaveLength(2);

    expect(rows[1]).toHaveTextContent("Acacia mangium");
    expect(rows[1]).toHaveTextContent("Tectona grandis");
  });

  it("keeps a rule when deletion is cancelled and deletes it when confirmed", async () => {
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

    await user.selectOptions(
      screen.getByLabelText(/^required partner species$/i),
      "2"
    );

    await user.click(
      screen.getByRole("button", {
        name: /add dependency$/i,
      })
    );

    const confirmSpy = vi.spyOn(window, "confirm");

    confirmSpy.mockReturnValueOnce(false);

    await user.click(screen.getByRole("button", { name: /delete/i }));

    expect(screen.getByText("Tectona grandis")).toBeInTheDocument();

    confirmSpy.mockReturnValueOnce(true);

    await user.click(screen.getByRole("button", { name: /delete/i }));

    expect(screen.queryByText("Tectona grandis")).not.toBeInTheDocument();

    expect(
      screen.getByText("No dependency rules have been configured.")
    ).toBeInTheDocument();
  });

  it("shows validation when required values are missing", async () => {
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
  });

  it("rejects a self dependency", async () => {
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

  it("shows an error when species loading fails", async () => {
    vi.mocked(getAllSpecies).mockRejectedValue(
      new Error("Unable to load species")
    );

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Unable to load species")).toBeInTheDocument();
    });

    expect(
      screen.getByRole("button", {
        name: /add dependency rule/i,
      })
    ).toBeDisabled();
  });
});
