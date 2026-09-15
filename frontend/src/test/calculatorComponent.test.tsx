import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import UserEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import type { GeoJsonObject } from "geojson";
import L from "leaflet";

import CalculatorHeader from "@/components/calculator/calculatorHeader";
import CalculatorSearch from "@/components/calculator/calculatorSearch";
import {
  CalculatorResult,
  CalculatorAggregate,
} from "@/components/calculator/calculatorResult";
import CalculatorTabs from "@/components/calculator/calculatorTabs";
import FarmLayers from "@/components/calculator/calculatorFarmLayers";
import FarmMap from "@/components/calculator/calculatorFarmMap";
import CombinedFarmMap from "@/components/calculator/calculatorCombinedMap";
import { useFarmMap } from "@/hooks/useFarmMap";
import { AGGREGATE_ID } from "@/hooks/useCalculator";
import type { FarmEstimationResult } from "@/hooks/useCalculator";

const { fitBoundsSpy } = vi.hoisted(() => ({ fitBoundsSpy: vi.fn() }));

vi.mock("react-leaflet", async () => {
  const React = await import("react");
  return {
    MapContainer: ({ children }: { children?: ReactNode }) =>
      React.createElement("div", { "data-testid": "map-container" }, children),
    TileLayer: () =>
      React.createElement("div", { "data-testid": "tile-layer" }),
    GeoJSON: ({ pointToLayer }: { pointToLayer?: unknown }) =>
      React.createElement("div", {
        "data-testid": pointToLayer ? "geojson-grid" : "geojson-boundary",
      }),
    Polyline: () => React.createElement("div", { "data-testid": "polyline" }),
    useMap: () => ({ fitBounds: fitBoundsSpy }),
  };
});

vi.mock("@/hooks/useFarmMap", () => ({
  useFarmMap: vi.fn(),
}));

const success = (farm_id: number): FarmEstimationResult => ({
  farm_id,
  status: "success",
  pre_slope_count: 100,
  aligned_count: 80,
  additional_sapling_count: 60,
  optimal_angle: 15,
});

const failed = (farm_id: number, message?: string): FarmEstimationResult => ({
  farm_id,
  status: "failed",
  message,
});

const boundaryGeoJSON: GeoJsonObject = {
  type: "Polygon",
  coordinates: [
    [
      [20.0, 10.0],
      [20.003, 10.0],
      [20.003, 10.002],
      [20.0, 10.002],
      [20.0, 10.0],
    ],
  ],
} as GeoJsonObject;

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
    additional_sapling_count: 50,
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

    expect(screen.getByText(/total sapling count/i)).toBeInTheDocument();
    expect(screen.getByText("80")).toBeInTheDocument();

    expect(
      screen.getByText(/saplings available to plant/i)
    ).toBeInTheDocument();
    expect(screen.getByText("50")).toBeInTheDocument();

    expect(screen.getByText(/optimal angle/i)).toBeInTheDocument();
    expect(screen.getByText("12.00°")).toBeInTheDocument();
  });

  it("renders a dash for missing numeric fields", () => {
    render(<CalculatorResult result={{ farm_id: 9, status: "success" }} />);

    expect(screen.getAllByText("-").length).toBeGreaterThanOrEqual(4);
  });
});

describe("CalculatorAggregate", () => {
  it("titles the card with the number of successful farms", () => {
    render(
      <CalculatorAggregate results={[success(1), success(2), failed(3)]} />
    );

    expect(screen.getByText(/aggregate of 2 farms/i)).toBeInTheDocument();
  });

  it("sums each numeric field across successful farms only", () => {
    render(
      <CalculatorAggregate results={[success(1), success(2), failed(3)]} />
    );

    expect(screen.getByText(/pre-slope sapling count/i)).toBeInTheDocument();
    expect(screen.getByText("200")).toBeInTheDocument();
    expect(screen.getByText(/total sapling count/i)).toBeInTheDocument();
    expect(screen.getByText("160")).toBeInTheDocument();
    expect(
      screen.getByText(/saplings available to plant/i)
    ).toBeInTheDocument();
    expect(screen.getByText("120")).toBeInTheDocument();
  });

  it("treats missing numeric fields as zero when summing", () => {
    const partial: FarmEstimationResult = {
      farm_id: 2,
      status: "success",
      pre_slope_count: 50,
      aligned_count: 40,
      optimal_angle: 10,
    };

    render(<CalculatorAggregate results={[success(1), partial]} />);

    expect(screen.getByText("150")).toBeInTheDocument();
    expect(screen.getByText("120")).toBeInTheDocument();
    expect(screen.getByText("60")).toBeInTheDocument();
  });

  it("does not render an optimal angle row", () => {
    render(<CalculatorAggregate results={[success(1), success(2)]} />);

    expect(screen.queryByText(/optimal angle/i)).not.toBeInTheDocument();
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
    expect(screen.getAllByRole("tab")).toHaveLength(4);
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

describe("CalculatorTabs (aggregate)", () => {
  it("renders an aggregate tab when more than one farm succeeds", () => {
    render(
      <CalculatorTabs
        results={[success(1), success(2)]}
        selectedFarmId={AGGREGATE_ID}
        onSelect={vi.fn()}
      />
    );

    const aggTab = screen.getByRole("tab", { name: /aggregate/i });
    expect(aggTab).toBeInTheDocument();
    expect(aggTab).toHaveAttribute("title", "Combined view of all farms");
  });

  it("shows the aggregate tab first, before the per-farm tabs", () => {
    render(
      <CalculatorTabs
        results={[success(1), success(2)]}
        selectedFarmId={AGGREGATE_ID}
        onSelect={vi.fn()}
      />
    );

    expect(screen.getAllByRole("tab")[0]).toHaveAccessibleName(/aggregate/i);
  });

  it("does not render an aggregate tab when only one farm succeeds", () => {
    render(
      <CalculatorTabs
        results={[success(1), failed(2)]}
        selectedFarmId={1}
        onSelect={vi.fn()}
      />
    );

    expect(
      screen.queryByRole("tab", { name: /aggregate/i })
    ).not.toBeInTheDocument();
    expect(screen.getAllByRole("tab")).toHaveLength(2);
  });

  it("calls onSelect with the aggregate id when the aggregate tab is clicked", async () => {
    const user = UserEvent.setup();
    const onSelect = vi.fn();

    render(
      <CalculatorTabs
        results={[success(1), success(2)]}
        selectedFarmId={1}
        onSelect={onSelect}
      />
    );

    await user.click(screen.getByRole("tab", { name: /aggregate/i }));

    expect(onSelect).toHaveBeenCalledWith(AGGREGATE_ID);
  });

  it("includes the aggregate tab in arrow-key navigation", async () => {
    const user = UserEvent.setup();
    const onSelect = vi.fn();

    render(
      <CalculatorTabs
        results={[success(1), success(2)]}
        selectedFarmId={AGGREGATE_ID}
        onSelect={onSelect}
      />
    );

    screen.getByRole("tab", { name: /aggregate/i }).focus();
    await user.keyboard("{ArrowRight}");

    expect(onSelect).toHaveBeenCalledWith(1);
  });

  it("wraps from the aggregate tab back to the last farm with ArrowLeft", async () => {
    const user = UserEvent.setup();
    const onSelect = vi.fn();

    render(
      <CalculatorTabs
        results={[success(1), success(2)]}
        selectedFarmId={AGGREGATE_ID}
        onSelect={onSelect}
      />
    );

    screen.getByRole("tab", { name: /aggregate/i }).focus();
    await user.keyboard("{ArrowLeft}");

    expect(onSelect).toHaveBeenCalledWith(2);
  });
});

describe("FarmLayers", () => {
  it("draws the boundary, one polyline per row, and the tree grid", () => {
    render(
      <FarmLayers
        boundary={boundaryGeoJSON}
        lines={[
          [
            [0, 0],
            [1, 1],
          ],
          [
            [2, 2],
            [3, 3],
          ],
        ]}
        grid={boundaryGeoJSON}
      />
    );

    expect(screen.getByTestId("geojson-boundary")).toBeInTheDocument();
    expect(screen.getAllByTestId("polyline")).toHaveLength(2);
    expect(screen.getByTestId("geojson-grid")).toBeInTheDocument();
  });

  it("omits the boundary layer when boundary is null", () => {
    render(<FarmLayers boundary={null} lines={[]} grid={boundaryGeoJSON} />);

    expect(screen.queryByTestId("geojson-boundary")).not.toBeInTheDocument();
    expect(screen.getByTestId("geojson-grid")).toBeInTheDocument();
  });

  it("omits the grid layer when grid is null", () => {
    render(<FarmLayers boundary={boundaryGeoJSON} lines={[]} grid={null} />);

    expect(screen.getByTestId("geojson-boundary")).toBeInTheDocument();
    expect(screen.queryByTestId("geojson-grid")).not.toBeInTheDocument();
  });

  it("renders no polylines when there are no lines", () => {
    render(
      <FarmLayers
        boundary={boundaryGeoJSON}
        lines={[]}
        grid={boundaryGeoJSON}
      />
    );

    expect(screen.queryByTestId("polyline")).not.toBeInTheDocument();
  });

  it("renders one polyline per line when a keyPrefix is supplied", () => {
    render(
      <FarmLayers
        boundary={null}
        grid={null}
        keyPrefix={7}
        lines={[
          [
            [0, 0],
            [1, 1],
          ],
          [
            [2, 2],
            [3, 3],
          ],
          [
            [4, 4],
            [5, 5],
          ],
        ]}
      />
    );

    expect(screen.getAllByTestId("polyline")).toHaveLength(3);
  });
});

describe("FarmMap", () => {
  it("renders the heading and layers when a boundary is present", () => {
    render(
      <FarmMap
        boundary={boundaryGeoJSON}
        grid={boundaryGeoJSON}
        optimalAngle={15}
        spacingY={3}
      />
    );

    expect(screen.getByText(/planting map/i)).toBeInTheDocument();
    expect(screen.getByTestId("geojson-boundary")).toBeInTheDocument();
    expect(screen.getByTestId("geojson-grid")).toBeInTheDocument();
  });

  it("renders nothing when there is no boundary", () => {
    const { container } = render(
      <FarmMap boundary={null} grid={null} optimalAngle={15} />
    );

    expect(container).toBeEmptyDOMElement();
  });
});

describe("CombinedFarmMap", () => {
  beforeEach(() => {
    fitBoundsSpy.mockClear();
    vi.mocked(useFarmMap).mockReturnValue({
      boundary: boundaryGeoJSON,
      grid: null,
      isLoading: false,
      error: null,
    });
    vi.spyOn(L, "geoJSON").mockReturnValue({
      getBounds: () =>
        L.latLngBounds([
          [10, 20],
          [10.002, 20.003],
        ]),
    } as unknown as ReturnType<typeof L.geoJSON>);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the combined map heading", () => {
    render(<CombinedFarmMap results={[success(1), success(2)]} />);

    expect(screen.getByText(/combined planting map/i)).toBeInTheDocument();
  });

  it("renders layers only for successful farms", async () => {
    render(<CombinedFarmMap results={[success(1), success(2), failed(3)]} />);

    await waitFor(() =>
      expect(screen.getAllByTestId("geojson-boundary")).toHaveLength(2)
    );
  });

  it("fits the map to the collected farm bounds", async () => {
    vi.mocked(useFarmMap).mockReturnValue({
      boundary: null,
      grid: null,
      isLoading: true,
      error: null,
    });

    const { rerender } = render(<CombinedFarmMap results={[success(1)]} />);

    vi.mocked(useFarmMap).mockReturnValue({
      boundary: boundaryGeoJSON,
      grid: null,
      isLoading: false,
      error: null,
    });
    rerender(<CombinedFarmMap results={[success(1)]} />);

    await waitFor(() => expect(fitBoundsSpy).toHaveBeenCalled());
  });
});
