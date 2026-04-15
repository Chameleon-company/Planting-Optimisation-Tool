import { it, expect, describe, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import UserEvent from "@testing-library/user-event";

import RecommendationSearch from "@/components/recommendations/recommendationSearch";
import RecommendationTable from "@/components/recommendations/recommendationTable";
import RecommendationRow from "@/components/recommendations/recommendationRow";
import ExcludedRow from "@/components/recommendations/excludedRow";
import ExcludedTable from "@/components/recommendations/excludedTable";

// Mock Data Generators
const mockRec = (id: number, score: number) => ({
  species_id: id,
  rank_overall: 1,
  species_common_name: "Test Tree",
  species_name: "Test scientific",
  score_mcda: score,
  key_reasons: ["Soil: Exact Match"],
});

const mockExcluded = (id: number) => ({
  id,
  species_common_name: "Excluded Tree",
  species_name: "Excludus scientificus",
  reasons: ["Too dry for this species"],
});

describe("RecommendationSearch", () => {
  it("calls onSearch with input value when button is clicked", async () => {
    const user = UserEvent.setup();
    const onSearch = vi.fn();

    render(<RecommendationSearch onSearch={onSearch} isLoading={false} />);

    await user.type(screen.getByRole("spinbutton"), "12");
    await user.click(
      screen.getByRole("button", { name: /generate recommendations/i })
    );

    expect(onSearch).toHaveBeenCalledWith("12");
  });

  it("disables button and shows loading text when isLoading is true", () => {
    render(<RecommendationSearch onSearch={vi.fn()} isLoading={true} />);

    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(screen.getByText(/analyzing suitability/i)).toBeInTheDocument();
  });
});

describe("RecommendationTable", () => {
  it("shows empty message when no data is provided", () => {
    render(
      <RecommendationTable
        title="Top Fit"
        data={[]}
        emptyMessage="No species found."
        type="top"
      />
    );

    expect(screen.getByText(/no species found/i)).toBeInTheDocument();
  });

  it("toggles all rows when Expand All is clicked", async () => {
    const user = UserEvent.setup();
    const data = [mockRec(1, 0.9), mockRec(2, 0.8)];

    render(
      <RecommendationTable
        title="Top Fit"
        data={data}
        emptyMessage="Empty"
        type="top"
      />
    );

    // Details should not be visible initially
    expect(screen.queryAllByText(/KEY FACTORS/i)).toHaveLength(0);

    // Click expand all
    await user.click(screen.getByRole("button", { name: /expand all/i }));

    // Details should now be visible for both rows
    expect(screen.getAllByText(/KEY FACTORS/i)).toHaveLength(2);

    // Button text should change
    expect(
      screen.getByRole("button", { name: /collapse all/i })
    ).toBeInTheDocument();
  });
});

describe("RecommendationRow", () => {
  it("renders details only when isExpanded is true", async () => {
    const user = UserEvent.setup();
    const onToggle = vi.fn();

    const { rerender } = render(
      <table>
        <tbody>
          <RecommendationRow
            item={mockRec(1, 0.9)}
            isExpanded={false}
            onToggle={onToggle}
          />
        </tbody>
      </table>
    );

    // Check for the A11y
    const button = screen.getByRole("button", { name: /details/i });
    expect(button).toHaveAttribute("aria-expanded", "false");

    expect(screen.queryByText(/KEY FACTORS/i)).not.toBeInTheDocument();

    await user.click(button);

    // Verify the interaction happened
    expect(onToggle).toHaveBeenCalledTimes(1);

    rerender(
      <table>
        <tbody>
          <RecommendationRow
            item={mockRec(1, 0.9)}
            isExpanded={true}
            onToggle={onToggle}
          />
        </tbody>
      </table>
    );

    expect(screen.getByText(/KEY FACTORS/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /hide/i })).toHaveAttribute(
      "aria-expanded",
      "true"
    );
  });
});

describe("ExcludedRow", () => {
  it("renders 'Details' button and expands to show reasons", async () => {
    const user = UserEvent.setup();
    const onToggle = vi.fn();
    const item = mockExcluded(1);

    const { rerender } = render(
      <table>
        <tbody>
          <ExcludedRow item={item} isExpanded={false} onToggle={onToggle} />
        </tbody>
      </table>
    );

    // Verify initial state
    expect(screen.queryByText(/Too dry/i)).not.toBeInTheDocument();

    // Check for the A11y
    const button = screen.getByRole("button", { name: /details/i });
    expect(button).toHaveAttribute("aria-expanded", "false");

    await user.click(button);

    // Verify the interaction happened
    expect(onToggle).toHaveBeenCalledTimes(1);

    // Simulate expansion
    rerender(
      <table>
        <tbody>
          <ExcludedRow item={item} isExpanded={true} onToggle={onToggle} />
        </tbody>
      </table>
    );

    expect(screen.getByText(/Too dry/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /hide/i })).toHaveAttribute(
      "aria-expanded",
      "true"
    );
  });
});

describe("ExcludedTable", () => {
  it("renders headers even when list is empty", () => {
    render(<ExcludedTable data={[]} />);
    expect(screen.getByText(/Excluded Species/i)).toBeInTheDocument();
  });

  it("renders the correct number of excluded rows", () => {
    const data = [mockExcluded(1), mockExcluded(2)];
    render(<ExcludedTable data={data} />);
    // Check for the common names of both mock items
    expect(screen.getAllByText(/Excluded Tree/i)).toHaveLength(2);
  });
});
