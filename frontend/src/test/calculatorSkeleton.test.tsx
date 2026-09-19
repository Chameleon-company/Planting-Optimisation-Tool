import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import CalculatorSkeleton from "@/components/calculator/calculatorSkeleton";

describe("CalculatorSkeleton", () => {
  it("renders the calculator loading skeleton", () => {
    render(<CalculatorSkeleton />);

    expect(screen.getByRole("status")).toBeInTheDocument();
  });
});
