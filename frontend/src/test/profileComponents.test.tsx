// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { Farm } from "@/hooks/useUserProfiles";
import { EnvironmentalProfile } from "@/hooks/useSearchProfiles";
import ProfileHeader from "@/components/profile/profileHeader";
import FarmList from "@/components/profile/profileFarms";
import FarmCard from "@/components/profile/profileAllCards";
import FarmPageNav from "@/components/profile/profilePageNav";
import ProfileEditActions from "@/components/profile/profileEditButtons";
import FarmSearchInput from "@/components/profile/profileSearchInput";
import EnvironmentalProfileCard from "@/components/profile/profileSearchedCard";
import FarmSearchPanel from "@/components/profile/profileSearchPanel";

// Mock Data for farms in useUserProfiles
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
  agroforestry_type: [{ name: "Silvopasture" }],
});

// Mock data for EnvironmentalProfile used in search result tests
const mockProfile = (id: number): EnvironmentalProfile => ({
  id,
  elevation_m: 149,
  ph: 6.5,
  slope: 4.2,
  latitude: -37.12345,
  longitude: 144.12345,
  area_ha: 0.402,
  coastal: true,
});

// Mock Functions
const mockUseAuth = vi.fn();
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

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
    render(<FarmCard farm={mockFarm(42)} />);
    // Verify the farm identifier and area display with correct formatting
    expect(screen.getByText("Farm #42")).toBeInTheDocument();
    expect(screen.getByText("12.345 ha")).toBeInTheDocument();
  });

  it("renders all environmental stats with correct units", () => {
    render(<FarmCard farm={mockFarm(1)} />);
    // Verify every core environmental metric appears with the right unit suffix
    expect(screen.getByText("800 mm")).toBeInTheDocument();
    expect(screen.getByText("22°C")).toBeInTheDocument();
    expect(screen.getByText("150 m")).toBeInTheDocument();
    expect(screen.getByText("6.5")).toBeInTheDocument();
    expect(screen.getByText("3.75°")).toBeInTheDocument();
    expect(screen.getByText("Loam")).toBeInTheDocument();
  });

  it("renders coordinates formatted to 5 decimal places", () => {
    render(<FarmCard farm={mockFarm(1)} />);
    // Latitude and longitude should be displayed with their full precision
    expect(screen.getByText(/-37.12345/)).toBeInTheDocument();
    expect(screen.getByText(/144.12345/)).toBeInTheDocument();
  });

  it("renders trait tags only for true boolean flags", () => {
    render(<FarmCard farm={mockFarm(1)} />);
    // Only truthy flags (coastal, nitrogen_fixing) should produce visible tags
    expect(screen.getByText("Coastal")).toBeInTheDocument();
    expect(screen.getByText("Nitrogen Fixing")).toBeInTheDocument();
    // False flags (riparian, shade_tolerant, bank_stabilising) must not render
    expect(screen.queryByText("Riparian")).not.toBeInTheDocument();
    expect(screen.queryByText("Shade Tolerant")).not.toBeInTheDocument();
    expect(screen.queryByText("Bank Stabilising")).not.toBeInTheDocument();
  });

  it("renders agroforestry type tags", () => {
    render(<FarmCard farm={mockFarm(1)} />);
    // Agroforestry classification tags should appear from the nested array
    expect(screen.getByText("Silvopasture")).toBeInTheDocument();
  });

  it("renders N/A for zero ph and slope values", () => {
    const farm = { ...mockFarm(1), ph: 0, slope: 0 };
    render(<FarmCard farm={farm} />);
    // Zero is treated as missing — a fallback "N/A" should be shown
    expect(screen.getByText("N/A")).toBeInTheDocument();
    // Slope fallback retains the degree symbol suffix
    expect(screen.getByText("N/A°")).toBeInTheDocument();
  });

  it("renders multiple agroforestry type tags when present", () => {
    const farm = {
      ...mockFarm(1),
      agroforestry_type: [{ name: "Silvopasture" }, { name: "Alley Cropping" }],
    };
    render(<FarmCard farm={farm} />);
    // Both agroforestry types should be rendered as separate tags
    expect(screen.getByText("Silvopasture")).toBeInTheDocument();
    expect(screen.getByText("Alley Cropping")).toBeInTheDocument();
  });
});

// FarmList Tests
describe("FarmList", () => {
  const setPage = vi.fn();

  it("shows loading indicator while farms are being fetched", () => {
    render(
      <FarmList
        farms={[]}
        isLoading={true}
        user={{ name: "John" }}
        page={0}
        totalPages={1}
        setPage={setPage}
      />
    );
    // A loading message should be shown while data is in flight
    expect(screen.getByText(/loading farms/i)).toBeInTheDocument();
  });

  it("shows login prompt when user is null", () => {
    render(
      <FarmList
        farms={[]}
        isLoading={false}
        user={null}
        page={0}
        totalPages={1}
        setPage={setPage}
      />
    );
    // Unauthenticated users should be told they need to log in
    expect(screen.getByText(/logged in/i)).toBeInTheDocument();
  });

  it("shows empty state message when user is logged in but has no farms", () => {
    render(
      <FarmList
        farms={[]}
        isLoading={false}
        user={{ name: "John" }}
        page={0}
        totalPages={1}
        setPage={setPage}
      />
    );
    // A clear "no farms" message should render when the farm array is empty
    expect(screen.getByText(/no farms found/i)).toBeInTheDocument();
  });

  it("renders a card for each farm in the data array", () => {
    render(
      <FarmList
        farms={[mockFarm(1), mockFarm(2)]}
        isLoading={false}
        user={{ name: "John" }}
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
    render(
      <FarmList
        farms={[mockFarm(1)]}
        isLoading={false}
        user={{ name: "John" }}
        page={0}
        totalPages={3}
        setPage={setPage}
      />
    );
    // The Previous button must be disabled when there are no earlier pages
    expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
  });

  it("disables the Next button on the last page", () => {
    render(
      <FarmList
        farms={[mockFarm(1)]}
        isLoading={false}
        user={{ name: "John" }}
        page={2}
        totalPages={3}
        setPage={setPage}
      />
    );
    // The Next button must be disabled when already on the final page
    expect(screen.getByRole("button", { name: /next/i })).toBeDisabled();
  });

  it("displays the correct current page number in the pagination info", () => {
    render(
      <FarmList
        farms={[mockFarm(1)]}
        isLoading={false}
        user={{ name: "John" }}
        page={1}
        totalPages={3}
        setPage={setPage}
      />
    );
    // Page index is zero-based internally but displayed as 1-based to the user
    expect(screen.getByText("Page 2 of 3")).toBeInTheDocument();
  });

  it("shows edit actions alongside the empty state for logged-in users", () => {
    render(
      <FarmList
        farms={[]}
        isLoading={false}
        user={{ name: "John" }}
        page={0}
        totalPages={0}
        setPage={setPage}
      />
    );
    // Even with no farms, the action buttons should render for authenticated users
    expect(screen.getByText(/no farms found/i)).toBeInTheDocument();
    // Admin role (set in beforeEach) means all three action buttons appear
    expect(screen.getByText(/Add/i)).toBeInTheDocument();
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

// ProfileEditActions Tests
describe("ProfileEditActions", () => {
  it("renders no buttons for regular logged-in users", () => {
    // A basic authenticated user (no elevated role) should only see Add
    mockUseAuth.mockReturnValue({ user: { name: "User", role: "officer" } });
    render(<ProfileEditActions />);
    expect(screen.queryByText(/Add/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Edit/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Delete/i)).not.toBeInTheDocument();
  });

  it("renders Edit button for supervisors", () => {
    // Supervisors have elevated write access but cannot delete
    mockUseAuth.mockReturnValue({
      user: { name: "Supervisor", role: "supervisor" },
    });
    render(<ProfileEditActions />);
    expect(screen.queryByText(/Add/i)).not.toBeInTheDocument();
    expect(screen.getByText(/Edit/i)).toBeInTheDocument();
    expect(screen.queryByText(/Delete/i)).not.toBeInTheDocument();
  });

  it("renders Add, Edit, and Delete buttons for admins", () => {
    // Admins have full CRUD access — all three action buttons should appear
    mockUseAuth.mockReturnValue({ user: { name: "Admin", role: "admin" } });
    render(<ProfileEditActions />);
    expect(screen.getByText(/Add/i)).toBeInTheDocument();
    expect(screen.getByText(/Edit/i)).toBeInTheDocument();
    expect(screen.getByText(/Delete/i)).toBeInTheDocument();
  });

  it("renders nothing when user is not logged in", () => {
    // Unauthenticated users should see no action controls at all
    mockUseAuth.mockReturnValue({ user: null });
    const { container } = render(<ProfileEditActions />);
    expect(container.firstChild).toBeNull();
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

// EnvironmentalProfileCard Tests
describe("EnvironmentalProfileCard", () => {
  it("renders the farm ID in the card header", () => {
    render(<EnvironmentalProfileCard profile={mockProfile(42)} />);
    // The profile ID should appear as the primary identifier in the card header
    expect(screen.getByText("Farm #42")).toBeInTheDocument();
  });

  it("renders area when provided", () => {
    render(<EnvironmentalProfileCard profile={mockProfile(1)} />);
    // Area should be formatted to 3 decimal places when the value is non-null
    expect(screen.getByText("0.402 ha")).toBeInTheDocument();
  });

  it("renders elevation, ph, and slope stats", () => {
    render(<EnvironmentalProfileCard profile={mockProfile(1)} />);
    // The three environmental stats should all be visible with correct values
    expect(screen.getByText(/149/)).toBeInTheDocument();
    expect(screen.getByText("6.5")).toBeInTheDocument();
    expect(screen.getByText(/4.20/)).toBeInTheDocument();
  });

  it("renders coordinates to 5 decimal places", () => {
    render(<EnvironmentalProfileCard profile={mockProfile(1)} />);
    // Coordinates must be shown with their full precision
    expect(screen.getByText(/-37.12345/)).toBeInTheDocument();
    expect(screen.getByText(/144.12345/)).toBeInTheDocument();
  });

  it("renders the Coastal trait tag when coastal is true", () => {
    render(<EnvironmentalProfileCard profile={mockProfile(1)} />);
    // A Coastal tag should appear when the coastal flag is set to true
    expect(screen.getByText("Coastal")).toBeInTheDocument();
  });

  it("does not render the Coastal tag when coastal is false", () => {
    const profile = { ...mockProfile(1), coastal: false };
    render(<EnvironmentalProfileCard profile={profile} />);
    // When coastal is false no tag should be rendered
    expect(screen.queryByText("Coastal")).not.toBeInTheDocument();
  });

  it("shows N/A for missing ph value", () => {
    const profile = { ...mockProfile(1), ph: undefined };
    render(<EnvironmentalProfileCard profile={profile} />);
    // Missing optional fields should fall back to a visible N/A placeholder
    expect(screen.getByText("N/A")).toBeInTheDocument();
  });
});

// FarmSearchPanel Tests
describe("FarmSearchPanel", () => {
  const baseProps = {
    query: "",
    setQuery: vi.fn(),
    profile: null,
    isLoading: false,
    error: null,
    user: { name: "John" },
  };

  it("renders the search input", () => {
    render(<FarmSearchPanel {...baseProps} />);
    // The search input should always be present regardless of query or auth state
    expect(
      screen.getByPlaceholderText(/search by farm id/i)
    ).toBeInTheDocument();
  });

  it("shows error message when error prop is set", () => {
    render(<FarmSearchPanel {...baseProps} error="Profile not found" />);
    // API or network errors should be surfaced to the user as a visible message
    expect(screen.getByText("Profile not found")).toBeInTheDocument();
  });

  it("shows loading indicator while a search is in progress", () => {
    render(<FarmSearchPanel {...baseProps} query="42" isLoading={true} />);
    // A loading message should appear whenever a query is active and loading
    expect(screen.getByText(/loading profile/i)).toBeInTheDocument();
  });

  it("renders the profile card when a result is returned", () => {
    render(
      <FarmSearchPanel {...baseProps} query="42" profile={mockProfile(42)} />
    );
    // A successful search result should display the profile card with the farm ID
    expect(screen.getByText("Farm #42")).toBeInTheDocument();
  });

  it("shows 'no profile found' when query is active but no result and user is logged in", () => {
    render(
      <FarmSearchPanel {...baseProps} query="999" profile={null} error={null} />
    );
    // When a query returns nothing (and there's no error) show a friendly empty state
    expect(screen.getByText(/no profile found/i)).toBeInTheDocument();
  });

  it("shows login required message when query is active but user is null", () => {
    render(
      <FarmSearchPanel
        {...baseProps}
        query="42"
        user={null}
        profile={null}
        error={null}
      />
    );
    // Unauthenticated users trying to search should be prompted to log in
    expect(screen.getByText(/must be logged in/i)).toBeInTheDocument();
  });

  it("does not show any search result state when query is empty", () => {
    render(<FarmSearchPanel {...baseProps} query="" />);
    // With no active query none of the result/empty/loading states should appear
    expect(screen.queryByText(/loading profile/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/no profile found/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/must be logged in/i)).not.toBeInTheDocument();
  });
});
