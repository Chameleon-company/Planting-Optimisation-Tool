import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { HelmetProvider } from "react-helmet-async";
import UserEvent from "@testing-library/user-event";

import CalculatorPage from "@/pages/CalculatorPage";

vi.mock("@/hooks/useCalculator", () => ({
  useCalculator: vi.fn(),
}));

import { useCalculator } from "@/hooks/useCalculator";

describe("CalculatorPage Integration", () => {
  it("does not show results before a search has been performed", () => {
    vi.mocked(useCalculator).mockReturnValue({
      result: null,
      isLoading: false,
      hasSearched: false,
      error: null,
    });

    render(
      <HelmetProvider>
        <CalculatorPage />
      </HelmetProvider>
    );

    expect(screen.getByText(/sapling calculator/i)).toBeInTheDocument();
    expect(screen.queryByText(/estimation results/i)).not.toBeInTheDocument();
  });

  it("shows results when estimation is complete", () => {
    vi.mocked(useCalculator).mockReturnValue({
      result: {
        id: 1,
        pre_slope_count: 100,
        aligned_count: 80,
        optimal_angle: 15,
      },
      isLoading: false,
      hasSearched: true,
      error: null,
    });

    render(
      <HelmetProvider>
        <CalculatorPage />
      </HelmetProvider>
    );

    expect(screen.getByText(/estimation results/i)).toBeInTheDocument();
    expect(screen.getByText("100")).toBeInTheDocument();
    expect(screen.getByText("80")).toBeInTheDocument();
    expect(screen.getByText("15.00°")).toBeInTheDocument();
  });

  it("shows an error message when an error exists", () => {
    vi.mocked(useCalculator).mockReturnValue({
      result: null,
      isLoading: false,
      hasSearched: false,
      error: "Farm not found",
    });

    render(
      <HelmetProvider>
        <CalculatorPage />
      </HelmetProvider>
    );

    expect(screen.getByText(/farm not found/i)).toBeInTheDocument();
  });

  it("updates input value (ID) when user types", async () => {
    const user = UserEvent.setup();

    vi.mocked(useCalculator).mockReturnValue({
      result: null,
      isLoading: false,
      hasSearched: false,
      error: null,
    });

    render(
      <HelmetProvider>
        <CalculatorPage />
      </HelmetProvider>
    );

    const input = screen.getByRole("spinbutton");
    await user.type(input, "50");

    expect(input).toHaveValue(50);
  });
});
