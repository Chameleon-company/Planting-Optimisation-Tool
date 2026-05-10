import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import UserEvent from "@testing-library/user-event";

import CalculatorHeader from "@/components/calculator/calculatorHeader";
import CalculatorSearch from "@/components/calculator/calculatorSearch";
import CalculatorResult from "@/components/calculator/calculatorResult";

describe("CalculatorHeader", () => {
  it("renders title and subtitle", () => {
    render(<CalculatorHeader />);

    expect(screen.getByText(/sapling calculator/i)).toBeInTheDocument();
    expect(
      screen.getByText(/estimate optimal sapling count for a farm/i)
    ).toBeInTheDocument();
  });
});

describe("CalculatorSearch", () => {
  it("calls onSearch with input value when button is clicked", async () => {
    const user = UserEvent.setup();
    const onSearch = vi.fn();

    render(<CalculatorSearch onSearch={onSearch} isLoading={false} />);

    await user.type(screen.getByLabelText(/farm id/i), "12");
    await user.click(
      screen.getByRole("button", { name: /generate planting plan/i })
    );

    expect(onSearch).toHaveBeenCalledWith("12", {
      spacingX: 3,
      spacingY: 3,
      maxSlope: 15,
    });
  });

  it("disables button and shows loading text when isLoading is true", () => {
    render(<CalculatorSearch onSearch={vi.fn()} isLoading={true} />);

    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(screen.getByText(/estimating saplings/i)).toBeInTheDocument();
  });
});

describe("CalculatorResult", () => {
  it("renders all result fields correctly", () => {
    const mockResult = {
      id: 1,
      pre_slope_count: 100,
      aligned_count: 80,
      optimal_angle: 12,
    };

    render(<CalculatorResult result={mockResult} />);

    expect(screen.getByText(/pre-slope sapling count/i)).toBeInTheDocument();
    expect(screen.getByText("100")).toBeInTheDocument();

    expect(screen.getByText(/final sapling count/i)).toBeInTheDocument();
    expect(screen.getByText("80")).toBeInTheDocument();

    expect(screen.getByText(/optimal angle/i)).toBeInTheDocument();
    expect(screen.getByText("12.00°")).toBeInTheDocument();
  });
});
