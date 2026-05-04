// @vitest-environment jsdom
import { it, expect, describe, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import UserEvent from "@testing-library/user-event";

import { SpeciesSelector } from "@/components/ahp/SpeciesSelector";
import AhpComparison from "@/components/ahp/AhpComparison";
import AhpResultsTable from "@/components/ahp/AhpResultsTable";

// Mock the species hook for the dropdown component
vi.mock("@/hooks/useAhp", () => ({
  useAhpSpecies: vi.fn().mockReturnValue({
    speciesList: [
      { id: 1, name: "Sci Name 1", common_name: "Tree 1" },
      { id: 2, name: "Sci Name 2", common_name: "Tree 2" },
    ],
    isLoading: false,
  }),
}));

describe("SpeciesSelector", () => {
  it("calls onSpeciesSelect with ID and Name when an option is chosen", async () => {
    const user = UserEvent.setup();
    const onSelect = vi.fn();

    render(<SpeciesSelector onSpeciesSelect={onSelect} />);

    const selectElement = screen.getByRole("combobox");
    await user.selectOptions(selectElement, "1"); // Value is the ID

    expect(onSelect).toHaveBeenCalledWith(1, "Tree 1");
  });

  it("disables the dropdown when isDisabled is true", () => {
    render(<SpeciesSelector onSpeciesSelect={vi.fn()} isDisabled={true} />);
    expect(screen.getByRole("combobox")).toBeDisabled();
  });
});

describe("AhpComparison", () => {
  it("completes matrix and calls onComplete on the final step", async () => {
    const user = UserEvent.setup();
    const onComplete = vi.fn();

    // Pass only 2 factors so there is only 1 comparison in the queue
    render(
      <AhpComparison
        factors={["Rainfall", "Temperature"]}
        speciesName="Test Tree"
        onComplete={onComplete}
        onCancel={vi.fn()}
      />
    );

    // Click the '3' button (favors Rainfall)
    const scaleButtons = screen.getAllByRole("button", { name: "3" });
    await user.click(scaleButtons[0]);

    // Finish the queue
    const nextButton = screen.getByRole("button", { name: /Next Comparison/i });
    await user.click(nextButton);

    // matrix[0][1] should be 3, matrix[1][0] should be 1/3
    expect(onComplete).toHaveBeenCalledWith([
      [1, 3],
      [1 / 3, 1],
    ]);
  });

  it("calls onCancel when cancel button is clicked", async () => {
    const user = UserEvent.setup();
    const onCancel = vi.fn();

    render(
      <AhpComparison
        factors={["A", "B"]}
        speciesName="Test"
        onComplete={vi.fn()}
        onCancel={onCancel}
      />
    );

    await user.click(screen.getByRole("button", { name: /Cancel/i }));
    expect(onCancel).toHaveBeenCalled();
  });
});

describe("AhpResultsTable", () => {
  const mockData = {
    weights: { Rainfall: 0.6, Temp: 0.4 },
    consistency_ratio: 0.05,
    is_consistent: true,
    message: "Calculated successfully",
  };

  it("shows acceptable message and Reset button if consistent", () => {
    render(
      <AhpResultsTable
        data={mockData}
        speciesName="Test"
        onReset={vi.fn()}
        onRetry={vi.fn()}
      />
    );

    expect(screen.getByText(/Acceptable/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Profile Another Species/i })
    ).toBeInTheDocument();
  });

  it("shows error message and Retry button if inconsistent", () => {
    const badData = {
      ...mockData,
      is_consistent: false,
      consistency_ratio: 0.25,
      message: "Inconsistent results",
    };

    render(
      <AhpResultsTable
        data={badData}
        speciesName="Test"
        onReset={vi.fn()}
        onRetry={vi.fn()}
      />
    );

    expect(screen.getByText(/Inconsistent/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Profile Again/i })
    ).toBeInTheDocument();
  });
});
