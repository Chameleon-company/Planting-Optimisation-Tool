import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { HelmetProvider } from "react-helmet-async";
import UserEvent from "@testing-library/user-event";

import CalculatorPage from "@/pages/CalculatorPage";

vi.mock("@/hooks/useCalculator", () => ({
  useCalculator: vi.fn(),
  DEFAULT_CALC_PARAMS: { spacingX: 3.0, spacingY: 3.0, maxSlope: 15.0 },
}));

vi.mock("@/hooks/useFarmMap", () => ({
  useFarmMap: vi.fn(() => ({
    boundary: null,
    grid: null,
    isLoading: false,
    error: null,
  })),
}));

vi.mock("@/components/calculator/FarmMap", () => ({
  default: () => null,
}));

import { useCalculator } from "@/hooks/useCalculator";

const idleHook = {
  result: null,
  isLoading: false,
  hasSearched: false,
  error: null,
};

describe("CalculatorPage Integration", () => {
  it("does not show results before a search has been performed", () => {
    vi.mocked(useCalculator).mockReturnValue(idleHook);

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
      ...idleHook,
      error: "Farm not found",
    });

    render(
      <HelmetProvider>
        <CalculatorPage />
      </HelmetProvider>
    );

    expect(screen.getByText(/farm not found/i)).toBeInTheDocument();
  });

  it("updates Farm ID input when user types", async () => {
    const user = UserEvent.setup();
    vi.mocked(useCalculator).mockReturnValue(idleHook);

    render(
      <HelmetProvider>
        <CalculatorPage />
      </HelmetProvider>
    );

    const input = screen.getByLabelText(/farm id/i);
    await user.type(input, "50");

    expect(input).toHaveValue(50);
  });

  it("renders spacing and slope inputs with default values", () => {
    vi.mocked(useCalculator).mockReturnValue(idleHook);

    render(
      <HelmetProvider>
        <CalculatorPage />
      </HelmetProvider>
    );

    expect(screen.getByLabelText(/spacing x/i)).toHaveValue(3);
    expect(screen.getByLabelText(/spacing y/i)).toHaveValue(3);
    expect(screen.getByLabelText(/max slope/i)).toHaveValue(15);
  });

  it("updates spacing X input when user changes value", async () => {
    const user = UserEvent.setup();
    vi.mocked(useCalculator).mockReturnValue(idleHook);

    render(
      <HelmetProvider>
        <CalculatorPage />
      </HelmetProvider>
    );

    const input = screen.getByLabelText(/spacing x/i);
    await user.clear(input);
    await user.type(input, "5");

    expect(input).toHaveValue(5);
  });
});
