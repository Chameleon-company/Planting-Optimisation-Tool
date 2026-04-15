// @vitest-environment jsdom
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter } from "react-router-dom"; // <-- Added MemoryRouter
import UserEvent from "@testing-library/user-event";

import AhpPage from "@/pages/admin/settings/AhpPage";

// Mock the entire custom hook suite
vi.mock("@/hooks/useAhp", () => ({
  useAhpFactors: vi.fn(),
  useAhpCalculation: vi.fn(),
  useAhpSpecies: vi.fn().mockReturnValue({
    speciesList: [{ id: 1, name: "Sci", common_name: "Test Tree" }],
    isLoading: false,
    error: null,
  }),
}));

import { useAhpFactors, useAhpCalculation } from "@/hooks/useAhp";

describe("AhpPage Integration", () => {
  it("disables start button until a species is selected", () => {
    vi.mocked(useAhpFactors).mockReturnValue({
      factorsList: { factors: ["A", "B"] },
      isLoading: false,
      error: null,
    });
    vi.mocked(useAhpCalculation).mockReturnValue({
      results: null,
      isCalculating: false,
      handleCalculate: vi.fn(),
      resetCalculation: vi.fn(),
      error: null,
    });

    // Wrapped in MemoryRouter
    render(
      <MemoryRouter>
        <HelmetProvider>
          <AhpPage />
        </HelmetProvider>
      </MemoryRouter>
    );

    const startBtn = screen.getByRole("button", { name: /Start Profiling/i });
    expect(startBtn).toBeDisabled();
    expect(
      screen.queryByText(/Which factor is more important/i)
    ).not.toBeInTheDocument();
  });

  it("opens comparison matrix when start button is clicked", async () => {
    const user = UserEvent.setup();

    vi.mocked(useAhpFactors).mockReturnValue({
      factorsList: { factors: ["A", "B"] },
      isLoading: false,
      error: null,
    });
    vi.mocked(useAhpCalculation).mockReturnValue({
      results: null,
      isCalculating: false,
      handleCalculate: vi.fn(),
      resetCalculation: vi.fn(),
      error: null,
    });

    // Wrapped in MemoryRouter
    render(
      <MemoryRouter>
        <HelmetProvider>
          <AhpPage />
        </HelmetProvider>
      </MemoryRouter>
    );

    // Select a species to enable the start button
    await user.selectOptions(screen.getByRole("combobox"), "1");

    const startBtn = screen.getByRole("button", { name: /Start Profiling/i });
    expect(startBtn).not.toBeDisabled();
    await user.click(startBtn);

    // The matrix UI should now be visible
    expect(
      screen.getByText(/Which factor is more important/i)
    ).toBeInTheDocument();
  });

  it("displays results table when calculations are complete", () => {
    vi.mocked(useAhpFactors).mockReturnValue({
      factorsList: { factors: ["A", "B"] },
      isLoading: false,
      error: null,
    });

    // Mock a finished calculation state
    vi.mocked(useAhpCalculation).mockReturnValue({
      results: {
        weights: { A: 0.5, B: 0.5 },
        consistency_ratio: 0,
        is_consistent: true,
        message: "Success",
      },
      isCalculating: false,
      handleCalculate: vi.fn(),
      resetCalculation: vi.fn(),
      error: null,
    });

    // Wrapped in MemoryRouter
    render(
      <MemoryRouter>
        <HelmetProvider>
          <AhpPage />
        </HelmetProvider>
      </MemoryRouter>
    );

    // Table headers should render
    expect(
      screen.getByRole("columnheader", { name: /Factor/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: /Weight/i })
    ).toBeInTheDocument();
  });
});
