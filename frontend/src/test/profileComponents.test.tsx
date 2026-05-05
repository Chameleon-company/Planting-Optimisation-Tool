// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, RenderOptions } from "@testing-library/react";
import { ReactElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { Farm } from "@/hooks/useUserProfiles";
import ProfileHeader from "@/components/profile/profileHeader";
import FarmList from "@/components/profile/profileFarms";
import FarmCard from "@/components/profile/profileCard";
import FarmPageNav from "@/components/profile/profilePageNav";
import FarmSearchInput from "@/components/profile/profileSearchInput";
import FarmSearchPanel from "@/components/profile/profileSearchPanel";

const mockFarm = (id: number): Farm => ({
  id,
  rainfall_mm: 800,
  temperature_celsius: 22,
  elevation_m: 150,
  ph: 6.5,
  soil_texture: { name: "Loam" },
  area_ha: 12.345,
  latitude: -37.12345,
  longitude: 144.12345,
  coastal: true,
  riparian: false,
  nitrogen_fixing: true,
  shade_tolerant: false,
  bank_stabilising: false,
  slope: 3.75,
  agroforestry_type: [{ id: 1, type_name: "Silvopasture" }],
});

// Mock Functions
const mockUseAuth = vi.fn();
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

function renderWithRouter(
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper">
) {
  return render(ui, { wrapper: MemoryRouter, ...options });
}

beforeEach(() => {
  // Reset to a logged-in admin before each test so most components render fully
  mockUseAuth.mockReturnValue({ user: { name: "Test User", role: "admin" } });
});

// ProfileHeader Tests
describe("ProfileHeader", () => {
  it("renders the page title", () => {
    render(<ProfileHeader userName="John" farmCount={3} />);
    // The main heading should always be visible regardless of auth state
    expect(screen.getByText("Environmental Profile")).toBeInTheDocument();
  });

  it("renders farmer name and farm count when user is logged in", () => {
    render(<ProfileHeader userName="John" farmCount={3} />);
    // Subtitle should show the farmer's name and plural "Farms" when count > 1
    expect(screen.getByText(/John · 3 Farms/i)).toBeInTheDocument();
  });

  it("renders singular Farm label when count is 1", () => {
    render(<ProfileHeader userName="John" farmCount={1} />);
    // Verify the singular form is used for exactly one farm
    expect(screen.getByText(/John · 1 Farm/i)).toBeInTheDocument();
  });

  it("renders empty subtitle when no farmer name is provided", () => {
    render(<ProfileHeader userName="" farmCount={0} />);
    // No separator dot should appear when there is no farmer info to display
    expect(screen.queryByText(/·/)).not.toBeInTheDocument();
  });
});

// FarmCard Tests
describe("FarmCard", () => {
  it("renders farm id and area", () => {
    render(<FarmCard farm={mockFarm(42)} isSearched={false} />);
    // Verify the farm identifier and area display with correct formatting
    expect(screen.getByText("Farm #42")).toBeInTheDocument();
    expect(screen.getByText("12.345 ha")).toBeInTheDocument();
  });

  it("renders all environmental stats with correct units", () => {
    render(<FarmCard farm={mockFarm(1)} isSearched={false} />);
    // Verify every core environmental metric appears with the right unit suffix
    expect(screen.getByText("800 mm")).toBeInTheDocument();
    expect(screen.getByText("22°C")).toBeInTheDocument();
    expect(screen.getByText("150 m")).toBeInTheDocument();
    expect(screen.getByText("6.5")).toBeInTheDocument();
    expect(screen.getByText("3.75°")).toBeInTheDocument();
    expect(screen.getByText("Loam")).toBeInTheDocument();
  });

  it("renders coordinates formatted to 5 decimal places", () => {
    render(<FarmCard farm={mockFarm(1)} isSearched={false} />);
    // Latitude and longitude should be displayed with their full precision
    expect(screen.getByText(/-37.12345/)).toBeInTheDocument();
    expect(screen.getByText(/144.12345/)).toBeInTheDocument();
  });

  it("renders trait tags only for true boolean flags", () => {
    render(<FarmCard farm={mockFarm(1)} isSearched={false} />);
    // Only truthy flags (coastal, nitrogen_fixing) should produce visible tags
    expect(screen.getByText("Coastal")).toBeInTheDocument();
    expect(screen.getByText("Nitrogen Fixing")).toBeInTheDocument();
    // False flags (riparian, shade_tolerant, bank_stabilising) must not render
    expect(screen.queryByText("Riparian")).not.toBeInTheDocument();
    expect(screen.queryByText("Shade Tolerant")).not.toBeInTheDocument();
    expect(screen.queryByText("Bank Stabilising")).not.toBeInTheDocument();
  });

  it("renders agroforestry type tags", () => {
    render(<FarmCard farm={mockFarm(1)} isSearched={false} />);
    // Agroforestry classification tags should appear from the nested array
    expect(screen.getByText("Silvopasture")).toBeInTheDocument();
  });

  it("renders N/A for zero ph and slope values", () => {
    const farm = { ...mockFarm(1), ph: 0, slope: 0 };
    render(<FarmCard farm={farm} isSearched={false} />);
    // Zero is treated as missing — a fallback "N/A" should be shown
    expect(screen.getByText("N/A")).toBeInTheDocument();
    // Slope fallback retains the degree symbol suffix
    expect(screen.getByText("N/A°")).toBeInTheDocument();
  });

  it("renders multiple agroforestry type tags when present", () => {
    const farm = {
      ...mockFarm(1),
      agroforestry_type: [
        { id: 1, type_name: "Silvopasture" },
        { id: 2, type_name: "Alley Cropping" },
      ],
    };
    render(<FarmCard farm={farm} isSearched={false} />);
    // Both agroforestry types should be rendered as separate tags
    expect(screen.getByText("Silvopasture")).toBeInTheDocument();
    expect(screen.getByText("Alley Cropping")).toBeInTheDocument();
  });

  it("applies the searchedCard class when isSearched is true", () => {
    const { container } = render(
      <FarmCard farm={mockFarm(1)} isSearched={true} />
    );
    // The wrapper div should carry the extra CSS class when rendered as a search result
    expect(container.firstChild).toHaveClass("searched-card");
  });

  it("does not apply the searchedCard class when isSearched is false", () => {
    const { container } = render(
      <FarmCard farm={mockFarm(1)} isSearched={false} />
    );
    // No extra class should be applied when the card is part of the regular farm list
    expect(container.firstChild).not.toHaveClass("searchedCard");
  });
});

// FarmList Tests
describe("FarmList", () => {
  const setPage = vi.fn();

  it("shows loading indicator while farms are being fetched", () => {
    renderWithRouter(
      <FarmList
        farms={[]}
        isLoading={true}
        page={0}
        totalPages={1}
        setPage={setPage}
      />
    );
    // A loading message should be shown while data is in flight
    expect(screen.getByText(/loading farms/i)).toBeInTheDocument();
  });

  it("shows empty state message when there are no farms", () => {
    renderWithRouter(
      <FarmList
        farms={[]}
        isLoading={false}
        page={0}
        totalPages={1}
        setPage={setPage}
      />
    );
    // A clear "no farms" message should render when the farm array is empty
    expect(screen.getByText(/no farms found/i)).toBeInTheDocument();
  });

  it("renders a card for each farm in the data array", () => {
    renderWithRouter(
      <FarmList
        farms={[mockFarm(1), mockFarm(2)]}
        isLoading={false}
        page={0}
        totalPages={1}
        setPage={setPage}
      />
    );
    // Each farm passed in should produce a visible FarmCard
    expect(screen.getByText("Farm #1")).toBeInTheDocument();
    expect(screen.getByText("Farm #2")).toBeInTheDocument();
  });

  it("disables the Previous button on the first page", () => {
    renderWithRouter(
      <FarmList
        farms={[mockFarm(1)]}
        isLoading={false}
        page={0}
        totalPages={3}
        setPage={setPage}
      />
    );
    // The Previous button must be disabled when there are no earlier pages
    expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
  });

  it("disables the Next button on the last page", () => {
    renderWithRouter(
      <FarmList
        farms={[mockFarm(1)]}
        isLoading={false}
        page={2}
        totalPages={3}
        setPage={setPage}
      />
    );
    // The Next button must be disabled when already on the final page
    expect(screen.getByRole("button", { name: /next/i })).toBeDisabled();
  });

  it("displays the correct current page number in the pagination info", () => {
    renderWithRouter(
      <FarmList
        farms={[mockFarm(1)]}
        isLoading={false}
        page={1}
        totalPages={3}
        setPage={setPage}
      />
    );
    // Page index is zero-based internally but displayed as 1-based to the user
    expect(screen.getByText("Page 2 of 3")).toBeInTheDocument();
  });
});

// FarmPageNav Tests
describe("FarmPageNav", () => {
  it("renders Previous, page info, and Next controls", () => {
    const setPage = vi.fn();
    render(<FarmPageNav page={1} totalPages={3} setPage={setPage} />);
    // All three navigation elements should be present at once
    expect(
      screen.getByRole("button", { name: /previous/i })
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /next/i })).toBeInTheDocument();
    expect(screen.getByText("Page 2 of 3")).toBeInTheDocument();
  });

  it("disables Previous on page 0", () => {
    const setPage = vi.fn();
    render(<FarmPageNav page={0} totalPages={3} setPage={setPage} />);
    // The Previous button must be disabled when there are no earlier pages
    expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
  });

  it("disables Next on the last page", () => {
    const setPage = vi.fn();
    render(<FarmPageNav page={2} totalPages={3} setPage={setPage} />);
    // The Next button must be disabled when already on the final page
    expect(screen.getByRole("button", { name: /next/i })).toBeDisabled();
  });

  it("enables both buttons when on a middle page", () => {
    const setPage = vi.fn();
    render(<FarmPageNav page={1} totalPages={3} setPage={setPage} />);
    // Neither button should be disabled when there are pages in both directions
    expect(
      screen.getByRole("button", { name: /previous/i })
    ).not.toBeDisabled();
    expect(screen.getByRole("button", { name: /next/i })).not.toBeDisabled();
  });
});

// FarmSearchInput Tests
describe("FarmSearchInput", () => {
  it("renders the search input with placeholder text", () => {
    render(
      <FarmSearchInput
        value=""
        onChange={vi.fn()}
        onClear={vi.fn()}
        isLoading={false}
      />
    );
    // The input should always be present with its descriptive placeholder
    expect(
      screen.getByPlaceholderText(/search by farm id/i)
    ).toBeInTheDocument();
  });

  it("reflects the current value in the input field", () => {
    render(
      <FarmSearchInput
        value="42"
        onChange={vi.fn()}
        onClear={vi.fn()}
        isLoading={false}
      />
    );
    // The controlled input should display whatever value is passed as a prop
    expect(screen.getByDisplayValue("42")).toBeInTheDocument();
  });

  it("shows a Clear button only when a value is present", () => {
    render(
      <FarmSearchInput
        value="42"
        onChange={vi.fn()}
        onClear={vi.fn()}
        isLoading={false}
      />
    );
    // The Clear button should only appear when there is text to clear
    expect(screen.getByText("Clear")).toBeInTheDocument();
  });

  it("hides the Clear button when value is empty", () => {
    render(
      <FarmSearchInput
        value=""
        onChange={vi.fn()}
        onClear={vi.fn()}
        isLoading={false}
      />
    );
    // With no query text the Clear button should not be rendered
    expect(screen.queryByText("Clear")).not.toBeInTheDocument();
  });

  it("disables the input while isLoading is true", () => {
    render(
      <FarmSearchInput
        value=""
        onChange={vi.fn()}
        onClear={vi.fn()}
        isLoading={true}
      />
    );
    // The input should be non-interactive while a search is in progress
    expect(screen.getByPlaceholderText(/search by farm id/i)).toBeDisabled();
  });
});

// FarmSearchPanel Tests
describe("FarmSearchPanel", () => {
  const baseProps = {
    query: "",
    setQuery: vi.fn(),
    profile: null as Farm | null,
    isLoading: false,
    error: null,
    user: { name: "John" },
  };

  it("renders the search input", () => {
    renderWithRouter(<FarmSearchPanel {...baseProps} />);
    // The search input should always be present regardless of query or auth state
    expect(
      screen.getByPlaceholderText(/search by farm id/i)
    ).toBeInTheDocument();
  });

  it("shows error message when error prop is set", () => {
    renderWithRouter(
      <FarmSearchPanel {...baseProps} error="Profile not found" />
    );
    // API or network errors should be surfaced to the user as a visible message
    expect(screen.getByText("Profile not found")).toBeInTheDocument();
  });

  it("shows loading indicator while a search is in progress", () => {
    renderWithRouter(
      <FarmSearchPanel {...baseProps} query="42" isLoading={true} />
    );
    // A loading message should appear whenever a query is active and loading
    expect(screen.getByText(/loading profile/i)).toBeInTheDocument();
  });

  it("renders the profile card when a result is returned", () => {
    renderWithRouter(
      <FarmSearchPanel {...baseProps} query="42" profile={mockFarm(42)} />
    );
    // A successful search result should display the profile card with the farm ID
    expect(screen.getByText("Farm #42")).toBeInTheDocument();
  });

  it("shows 'no profile found' when query is active but no result and user is logged in", () => {
    renderWithRouter(
      <FarmSearchPanel {...baseProps} query="999" profile={null} error={null} />
    );
    // When a query returns nothing (and there's no error) show a friendly empty state
    expect(screen.getByText(/no profile found/i)).toBeInTheDocument();
  });

  it("shows login required message when query is active but user is null", () => {
    mockUseAuth.mockReturnValue({
      user: null,
    });

    renderWithRouter(
      <FarmSearchPanel
        query="42"
        setQuery={vi.fn()}
        profile={null}
        isLoading={false}
        error={null}
      />
    );

    // Unauthenticated users trying to search should be prompted to log in
    expect(screen.getByText(/must be logged in/i)).toBeInTheDocument();
  });

  it("does not show any search result state when query is empty", () => {
    renderWithRouter(<FarmSearchPanel {...baseProps} query="" />);
    // With no active query none of the result/empty/loading states should appear
    expect(screen.queryByText(/loading profile/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/no profile found/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/must be logged in/i)).not.toBeInTheDocument();
  });
});
