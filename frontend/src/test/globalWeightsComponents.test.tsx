import { it, expect, describe, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import UserEvent from "@testing-library/user-event";
import GlobalWeightsHeader from "@/components/globalWeights/GlobalWeightsHeader";
import GlobalWeightRunTable from "@/components/globalWeights/GlobalWeightRunTable";
import GlobalWeightRunRow from "@/components/globalWeights/GlobalWeightRunRow";

// Mock Data Generators
const mockRun = (id: string) => ({
  run_id: id,
  created_at: "2024-01-01T12:00:00Z",
  bootstraps: 100,
  bootstrap_early_stopped: true,
  source: "User Upload",
});

const mockWeightItem = (feature: string) => ({
  feature,
  mean_weight: 0.25,
  ci_lower: 0.2,
  ci_upper: 0.3,
  ci_width: 0.1,
  touches_zero: false,
});

describe("GlobalWeightsHeader", () => {
  it("renders the title and description", () => {
    render(<GlobalWeightsHeader />);
    expect(
      screen.getByRole("heading", { name: /^Global Weights$/i })
    ).toBeInTheDocument();
    expect(screen.getByText(/Process EPI data/i)).toBeInTheDocument();
  });
});

describe("GlobalWeightRunTable", () => {
  it("shows placeholder message when no runs are available", () => {
    render(
      <GlobalWeightRunTable
        runs={[]}
        fetchDetails={vi.fn()}
        deleteRun={vi.fn()}
      />
    );
    expect(
      screen.getByText(/No global weight runs available/i)
    ).toBeInTheDocument();
  });

  it("renders rows for each run provided", () => {
    const runs = [mockRun("run1-uuid"), mockRun("run2-uuid")];
    render(
      <GlobalWeightRunTable
        runs={runs}
        fetchDetails={vi.fn()}
        deleteRun={vi.fn()}
      />
    );
    const rows = screen.getAllByRole("row");
    expect(rows).toHaveLength(3);

    // The component renders: {run.run_id.split("-")[0]}
    expect(screen.getByText(/run1/i)).toBeInTheDocument();
    expect(screen.getByText(/run2/i)).toBeInTheDocument();

    // Verify other column data to ensure the row is fully rendered
    expect(screen.getAllByText(/User Upload/i)).toHaveLength(2);
  });
});

describe("GlobalWeightRunRow", () => {
  const run = mockRun("test-uuid-1234");

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock window.confirm for delete actions
    vi.stubGlobal(
      "confirm",
      vi.fn(() => true)
    );
  });

  it("calls fetchDetails and displays table when expanded", async () => {
    const user = UserEvent.setup();
    const fetchDetails = vi
      .fn()
      .mockResolvedValue([mockWeightItem("Rainfall")]);
    const onToggle = vi.fn();

    const { rerender } = render(
      <table>
        <tbody>
          <GlobalWeightRunRow
            run={run}
            isExpanded={false}
            onToggle={onToggle}
            fetchDetails={fetchDetails}
            onDelete={vi.fn()}
          />
        </tbody>
      </table>
    );

    // Click to expand
    await user.click(screen.getByRole("button", { name: /view weights/i }));
    expect(onToggle).toHaveBeenCalled();

    // Simulate parent state update to expanded
    rerender(
      <table>
        <tbody>
          <GlobalWeightRunRow
            run={run}
            isExpanded={true}
            onToggle={onToggle}
            fetchDetails={fetchDetails}
            onDelete={vi.fn()}
          />
        </tbody>
      </table>
    );

    expect(screen.getByText(/Loading weights.../i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Rainfall")).toBeInTheDocument();
      expect(screen.getByText("0.250")).toBeInTheDocument();
    });
  });

  it("calls onDelete when delete button is clicked and confirmed", async () => {
    const user = UserEvent.setup();
    const onDelete = vi.fn();
    const confirmSpy = vi.spyOn(window, "confirm");

    render(
      <table>
        <tbody>
          <GlobalWeightRunRow
            run={run}
            isExpanded={false}
            onToggle={vi.fn()}
            fetchDetails={vi.fn()}
            onDelete={onDelete}
          />
        </tbody>
      </table>
    );

    await user.click(screen.getByRole("button", { name: /delete/i }));

    expect(confirmSpy).toHaveBeenCalledWith(
      expect.stringContaining(
        "Are you sure you want to delete this global weight run? This cannot be undone."
      )
    );
    expect(onDelete).toHaveBeenCalledWith(run.run_id);
  });
});
