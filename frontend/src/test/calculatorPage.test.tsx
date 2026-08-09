import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import UserEvent from "@testing-library/user-event";

import CalculatorHeader from "@/components/calculator/calculatorHeader";
import CalculatorSearch from "@/components/calculator/calculatorSearch";
import CalculatorResult from "@/components/calculator/calculatorResult";
import CalculatorTabs from "@/components/calculator/calculatorTabs";
import type { FarmEstimationResult } from "@/hooks/useCalculator";

const success = (farm_id: number): FarmEstimationResult => ({
  farm_id,
  status: "success",
  pre_slope_count: 100,
  aligned_count: 80,
  optimal_angle: 15,
});

const failed = (farm_id: number, message?: string): FarmEstimationResult => ({
  farm_id,
  status: "failed",
  message,
});

describe("CalculatorHeader", () => {
  it("renders title and subtitle", () => {
    render(<CalculatorHeader />);

    expect(screen.getByText(/sapling calculator/i)).toBeInTheDocument();
    expect(
      screen.getByText(/estimate optimal sapling count/i)
    ).toBeInTheDocument();
  });
});

describe("CalculatorSearch", () => {
  it("calls onSearch with a single parsed id when the button is clicked", async () => {
    const user = UserEvent.setup();
    const onSearch = vi.fn();

    render(<CalculatorSearch onSearch={onSearch} isLoading={false} />);

    await user.type(screen.getByLabelText(/farm id/i), "12");
    await user.click(
      screen.getByRole("button", { name: /generate planting plan/i })
    );

    expect(onSearch).toHaveBeenCalledWith([12], {
      spacingX: 3,
      spacingY: 3,
      maxSlope: 15,
    });
  });

  it("parses a comma/space separated list into multiple ids", async () => {
    const user = UserEvent.setup();
    const onSearch = vi.fn();

    render(<CalculatorSearch onSearch={onSearch} isLoading={false} />);

    await user.type(screen.getByLabelText(/farm id/i), "1, 2 3");
    await user.click(
      screen.getByRole("button", { name: /generate planting plan/i })
    );

    expect(onSearch).toHaveBeenCalledWith(
      [1, 2, 3],
      expect.objectContaining({ spacingX: 3, spacingY: 3, maxSlope: 15 })
    );
  });

  it("de-duplicates ids and drops non-positive/invalid values", async () => {
    const user = UserEvent.setup();
    const onSearch = vi.fn();

    render(<CalculatorSearch onSearch={onSearch} isLoading={false} />);

    await user.type(screen.getByLabelText(/farm id/i), "2, 2, 0, -1, abc, 3");
    await user.click(
      screen.getByRole("button", { name: /generate planting plan/i })
    );

    expect(onSearch).toHaveBeenCalledWith([2, 3], expect.any(Object));
  });

  it("searches when the user presses Enter in the id field", async () => {
    const user = UserEvent.setup();
    const onSearch = vi.fn();

    render(<CalculatorSearch onSearch={onSearch} isLoading={false} />);

    await user.type(screen.getByLabelText(/farm id/i), "7{enter}");

    expect(onSearch).toHaveBeenCalledWith([7], expect.any(Object));
  });

  it("keeps the button disabled while the id field is empty", () => {
    render(<CalculatorSearch onSearch={vi.fn()} isLoading={false} />);

    expect(
      screen.getByRole("button", { name: /generate planting plan/i })
    ).toBeDisabled();
  });

  it("does not call onSearch when there are no valid ids", async () => {
    const user = UserEvent.setup();
    const onSearch = vi.fn();

    render(<CalculatorSearch onSearch={onSearch} isLoading={false} />);

    await user.type(screen.getByLabelText(/farm id/i), "abc, -5");
    await user.click(screen.getByRole("button"));

    expect(onSearch).not.toHaveBeenCalled();
  });

  it("disables the button and shows loading text when isLoading is true", () => {
    render(<CalculatorSearch onSearch={vi.fn()} isLoading={true} />);

    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(screen.getByText(/estimating saplings/i)).toBeInTheDocument();
  });
});

describe("CalculatorResult", () => {
  const mockResult: FarmEstimationResult = {
    farm_id: 1,
    status: "success",
    pre_slope_count: 100,
    aligned_count: 80,
    optimal_angle: 12,
  };

  it("renders the farm id in the heading", () => {
    render(<CalculatorResult result={mockResult} />);

    expect(
      screen.getByText(/estimation results - farm 1/i)
    ).toBeInTheDocument();
  });

  it("renders all result fields correctly", () => {
    render(<CalculatorResult result={mockResult} />);

    expect(screen.getByText(/pre-slope sapling count/i)).toBeInTheDocument();
    expect(screen.getByText("100")).toBeInTheDocument();

    expect(screen.getByText(/final sapling count/i)).toBeInTheDocument();
    expect(screen.getByText("80")).toBeInTheDocument();

    expect(screen.getByText(/optimal angle/i)).toBeInTheDocument();
    expect(screen.getByText("12.00°")).toBeInTheDocument();
  });

  it("renders a dash for missing numeric fields", () => {
    render(<CalculatorResult result={{ farm_id: 9, status: "success" }} />);

    // pre-slope, final count, and optimal angle all fall back to "-"
    expect(screen.getAllByText("-").length).toBeGreaterThanOrEqual(3);
  });
});

describe("CalculatorTabs", () => {
  it("renders nothing when there is a single result", () => {
    const { container } = render(
      <CalculatorTabs
        results={[success(1)]}
        selectedFarmId={1}
        onSelect={vi.fn()}
      />
    );

    expect(container).toBeEmptyDOMElement();
    expect(screen.queryByRole("tablist")).not.toBeInTheDocument();
  });

  it("renders a tab for each farm when there are multiple results", () => {
    render(
      <CalculatorTabs
        results={[success(1), success(2), failed(3)]}
        selectedFarmId={1}
        onSelect={vi.fn()}
      />
    );

    expect(screen.getByRole("tablist")).toBeInTheDocument();
    expect(screen.getAllByRole("tab")).toHaveLength(3);
    expect(screen.getByRole("tab", { name: /farm 1/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /farm 3/i })).toBeInTheDocument();
  });

  it("marks the selected farm's tab as active", () => {
    render(
      <CalculatorTabs
        results={[success(1), success(2)]}
        selectedFarmId={2}
        onSelect={vi.fn()}
      />
    );

    expect(screen.getByRole("tab", { name: /farm 2/i })).toHaveAttribute(
      "aria-selected",
      "true"
    );
    expect(screen.getByRole("tab", { name: /farm 1/i })).toHaveAttribute(
      "aria-selected",
      "false"
    );
  });

  it("uses the failure message as the tab title for failed farms", () => {
    render(
      <CalculatorTabs
        results={[success(1), failed(2, "No boundary data")]}
        selectedFarmId={1}
        onSelect={vi.fn()}
      />
    );

    expect(screen.getByRole("tab", { name: /farm 2/i })).toHaveAttribute(
      "title",
      "No boundary data"
    );
  });

  it("calls onSelect with the farm id when a tab is clicked", async () => {
    const user = UserEvent.setup();
    const onSelect = vi.fn();

    render(
      <CalculatorTabs
        results={[success(1), success(2)]}
        selectedFarmId={1}
        onSelect={onSelect}
      />
    );

    await user.click(screen.getByRole("tab", { name: /farm 2/i }));

    expect(onSelect).toHaveBeenCalledWith(2);
  });
});
