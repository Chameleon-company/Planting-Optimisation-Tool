import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { HelmetProvider } from "react-helmet-async";
import UserEvent from "@testing-library/user-event";

import CalculatorPage from "@/pages/CalculatorPage";
import type { FarmEstimationResult } from "@/hooks/useCalculator";

vi.mock("@/hooks/useCalculator", () => ({
  useCalculator: vi.fn(),
  DEFAULT_CALC_PARAMS: { spacingX: 3.0, spacingY: 3.0, maxSlope: 15.0 },
  AGGREGATE_ID: -1,
}));

vi.mock("@/hooks/useFarmMap", () => ({
  useFarmMap: vi.fn(() => ({
    boundary: null,
    grid: null,
    isLoading: false,
    error: null,
  })),
}));

vi.mock("@/components/calculator/calculatorFarmMap", () => ({
  default: () => null,
}));

vi.mock("@/components/calculator/calculatorCombinedMap", () => ({
  default: () => null,
}));

import { useCalculator } from "@/hooks/useCalculator";

const idleHook = {
  results: [],
  isLoading: false,
  hasSearched: false,
  error: null,
};

const success = (
  farm_id: number,
  aligned_count: number
): FarmEstimationResult => ({
  farm_id,
  status: "success",
  pre_slope_count: 100,
  aligned_count,
  additional_sapling_count: aligned_count - 20,
  optimal_angle: 15,
});

const renderPage = () =>
  render(
    <HelmetProvider>
      <CalculatorPage />
    </HelmetProvider>
  );

describe("CalculatorPage Integration", () => {
  it("does not show results before a search has been performed", () => {
    vi.mocked(useCalculator).mockReturnValue(idleHook);

    renderPage();

    expect(screen.getByText(/sapling calculator/i)).toBeInTheDocument();
    expect(screen.queryByText(/estimation results/i)).not.toBeInTheDocument();
  });

  it("shows the results when estimation is complete", () => {
    vi.mocked(useCalculator).mockReturnValue({
      ...idleHook,
      hasSearched: true,
      results: [success(1, 80)],
    });

    renderPage();

    expect(
      screen.getByText(/estimation results - farm 1/i)
    ).toBeInTheDocument();
    expect(screen.getByText("100")).toBeInTheDocument();
    expect(screen.getByText("80")).toBeInTheDocument();
    expect(screen.getByText("60")).toBeInTheDocument();
    expect(screen.getByText("15.00°")).toBeInTheDocument();
  });

  it("does not render tabs for a single result", () => {
    vi.mocked(useCalculator).mockReturnValue({
      ...idleHook,
      hasSearched: true,
      results: [success(1, 80)],
    });

    renderPage();

    expect(screen.queryByRole("tablist")).not.toBeInTheDocument();
  });

  it("renders tabs and switches farms when there are multiple results", async () => {
    const user = UserEvent.setup();
    vi.mocked(useCalculator).mockReturnValue({
      ...idleHook,
      hasSearched: true,
      results: [success(1, 80), success(2, 55)],
    });

    renderPage();

    expect(screen.getByText(/aggregate of 2 farms/i)).toBeInTheDocument();
    expect(screen.getByRole("tablist")).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: /farm 2/i }));

    expect(
      screen.getByText(/estimation results - farm 2/i)
    ).toBeInTheDocument();
    expect(screen.getByText("55")).toBeInTheDocument();
    expect(screen.getByText("35")).toBeInTheDocument();
  });

  it("aggregate totals equal the sum of the individual per-farm tabs", async () => {
    const user = UserEvent.setup();
    const farmA = success(1, 80);
    const farmB = success(2, 55);
    vi.mocked(useCalculator).mockReturnValue({
      ...idleHook,
      hasSearched: true,
      results: [farmA, farmB],
    });

    renderPage();

    expect(screen.getByText(/aggregate of 2 farms/i)).toBeInTheDocument();

    const expectedPreSlope =
      (farmA.pre_slope_count ?? 0) + (farmB.pre_slope_count ?? 0);
    const expectedAligned =
      (farmA.aligned_count ?? 0) + (farmB.aligned_count ?? 0);
    const expectedAdditional =
      (farmA.additional_sapling_count ?? 0) +
      (farmB.additional_sapling_count ?? 0);

    expect(screen.getByText(String(expectedPreSlope))).toBeInTheDocument();
    expect(screen.getByText(String(expectedAligned))).toBeInTheDocument();
    expect(screen.getByText(String(expectedAdditional))).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: /farm 1/i }));
    expect(
      screen.getByText(/estimation results - farm 1/i)
    ).toBeInTheDocument();
    expect(screen.getByText(String(farmA.pre_slope_count))).toBeInTheDocument();
    expect(screen.getByText(String(farmA.aligned_count))).toBeInTheDocument();
    expect(
      screen.getByText(String(farmA.additional_sapling_count))
    ).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: /farm 2/i }));
    expect(
      screen.getByText(/estimation results - farm 2/i)
    ).toBeInTheDocument();
    expect(screen.getByText(String(farmB.pre_slope_count))).toBeInTheDocument();
    expect(screen.getByText(String(farmB.aligned_count))).toBeInTheDocument();
    expect(
      screen.getByText(String(farmB.additional_sapling_count))
    ).toBeInTheDocument();

    expect(expectedPreSlope).toBe(
      (farmA.pre_slope_count ?? 0) + (farmB.pre_slope_count ?? 0)
    );
    expect(expectedAligned).toBe(
      (farmA.aligned_count ?? 0) + (farmB.aligned_count ?? 0)
    );
    expect(expectedAdditional).toBe(
      (farmA.additional_sapling_count ?? 0) +
        (farmB.additional_sapling_count ?? 0)
    );
  });

  it("focuses the first successful farm even when earlier farms failed", () => {
    vi.mocked(useCalculator).mockReturnValue({
      ...idleHook,
      hasSearched: true,
      results: [
        { farm_id: 1, status: "failed", message: "No boundary data" },
        success(2, 80),
      ],
    });

    renderPage();

    expect(
      screen.getByText(/estimation results - farm 2/i)
    ).toBeInTheDocument();
  });

  it("shows a per-farm failure panel when a failed tab is selected", async () => {
    const user = UserEvent.setup();
    vi.mocked(useCalculator).mockReturnValue({
      ...idleHook,
      hasSearched: true,
      results: [
        success(1, 80),
        { farm_id: 2, status: "failed", message: "No boundary data" },
      ],
    });

    renderPage();

    await user.click(screen.getByRole("tab", { name: /farm 2/i }));

    expect(screen.getByText(/farm 2 failed/i)).toBeInTheDocument();
    expect(screen.getByText(/no boundary data/i)).toBeInTheDocument();
  });

  it("shows a top-level error message when the request itself fails", () => {
    vi.mocked(useCalculator).mockReturnValue({
      ...idleHook,
      error: "Please log in to continue.",
    });

    renderPage();

    expect(screen.getByText(/please log in to continue/i)).toBeInTheDocument();
  });

  it("updates Farm ID input when user types", async () => {
    const user = UserEvent.setup();
    vi.mocked(useCalculator).mockReturnValue(idleHook);

    renderPage();

    const input = screen.getByLabelText(/farm id/i);
    await user.type(input, "50");

    expect(input).toHaveValue("50");
  });

  it("renders spacing and slope inputs with default values", () => {
    vi.mocked(useCalculator).mockReturnValue(idleHook);

    renderPage();

    expect(screen.getByLabelText(/spacing x/i)).toHaveValue(3);
    expect(screen.getByLabelText(/spacing y/i)).toHaveValue(3);
    expect(screen.getByLabelText(/max slope/i)).toHaveValue(15);
  });

  it("updates spacing X input when user changes value", async () => {
    const user = UserEvent.setup();
    vi.mocked(useCalculator).mockReturnValue(idleHook);

    renderPage();

    const input = screen.getByLabelText(/spacing x/i);
    await user.clear(input);
    await user.type(input, "5");

    expect(input).toHaveValue(5);
  });

  it("defaults to the aggregate view when more than one farm succeeds", () => {
    vi.mocked(useCalculator).mockReturnValue({
      ...idleHook,
      hasSearched: true,
      results: [success(1, 80), success(2, 55)],
    });

    renderPage();

    expect(screen.getByText(/aggregate of 2 farms/i)).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /aggregate/i })).toHaveAttribute(
      "aria-selected",
      "true"
    );
  });

  it("returns to the aggregate view after viewing a single farm", async () => {
    const user = UserEvent.setup();
    vi.mocked(useCalculator).mockReturnValue({
      ...idleHook,
      hasSearched: true,
      results: [success(1, 80), success(2, 55)],
    });

    renderPage();

    await user.click(screen.getByRole("tab", { name: /farm 1/i }));
    expect(
      screen.getByText(/estimation results - farm 1/i)
    ).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: /aggregate/i }));
    expect(screen.getByText(/aggregate of 2 farms/i)).toBeInTheDocument();
  });

  it("does not show an aggregate tab or card when only one farm succeeds", () => {
    vi.mocked(useCalculator).mockReturnValue({
      ...idleHook,
      hasSearched: true,
      results: [
        success(1, 80),
        { farm_id: 2, status: "failed", message: "No boundary data" },
      ],
    });

    renderPage();

    expect(screen.queryByText(/aggregate of/i)).not.toBeInTheDocument();
    expect(
      screen.queryByRole("tab", { name: /aggregate/i })
    ).not.toBeInTheDocument();
    expect(
      screen.getByText(/estimation results - farm 1/i)
    ).toBeInTheDocument();
  });
});
