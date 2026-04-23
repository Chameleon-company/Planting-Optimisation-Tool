// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Farm } from "@/hooks/useUserProfiles";
import { EnvironmentalProfile } from "@/hooks/useSearchProfiles";
import FarmList from "@/components/profile/profileFarms";
import FarmPageNav from "@/components/profile/profilePageNav";
import FarmSearchInput from "@/components/profile/profileSearchInput";
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
  // Reset to a logged-in admin before each test so all action buttons are available
  mockUseAuth.mockReturnValue({ user: { name: "Test User", role: "admin" } });
});

// FarmList Interaction Tests
describe("FarmList interactions", () => {
  it("calls setPage when the Next button is clicked", async () => {
    const user = userEvent.setup();
    const setPage = vi.fn();
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
    // Clicking Next should invoke the page-change callback
    await user.click(screen.getByRole("button", { name: /next/i }));
    expect(setPage).toHaveBeenCalled();
  });

  it("calls setPage when the Previous button is clicked on a non-first page", async () => {
    const user = userEvent.setup();
    const setPage = vi.fn();
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
    // Clicking Previous should invoke the page-change callback
    await user.click(screen.getByRole("button", { name: /previous/i }));
    expect(setPage).toHaveBeenCalled();
  });
});

// FarmPageNav Interaction Tests
describe("FarmPageNav interactions", () => {
  it("calls setPage with page - 1 when Previous is clicked", async () => {
    const user = userEvent.setup();
    const setPage = vi.fn();
    render(<FarmPageNav page={2} totalPages={3} setPage={setPage} />);
    // Clicking Previous should decrement the page by one
    await user.click(screen.getByRole("button", { name: /previous/i }));
    expect(setPage).toHaveBeenCalledWith(1);
  });

  it("calls setPage with page + 1 when Next is clicked", async () => {
    const user = userEvent.setup();
    const setPage = vi.fn();
    render(<FarmPageNav page={0} totalPages={3} setPage={setPage} />);
    // Clicking Next should increment the page index by one
    await user.click(screen.getByRole("button", { name: /next/i }));
    expect(setPage).toHaveBeenCalledWith(1);
  });

  it("does not call setPage when Previous is clicked while disabled", async () => {
    const user = userEvent.setup();
    const setPage = vi.fn();
    render(<FarmPageNav page={0} totalPages={3} setPage={setPage} />);
    // A disabled Previous button should not trigger the callback
    await user.click(screen.getByRole("button", { name: /previous/i }));
    expect(setPage).not.toHaveBeenCalled();
  });

  it("does not call setPage when Next is clicked while disabled", async () => {
    const user = userEvent.setup();
    const setPage = vi.fn();
    render(<FarmPageNav page={2} totalPages={3} setPage={setPage} />);
    // A disabled Next button should not trigger the callback
    await user.click(screen.getByRole("button", { name: /next/i }));
    expect(setPage).not.toHaveBeenCalled();
  });
});

// FarmSearchInput Interaction Tests
describe("FarmSearchInput interactions", () => {
  it("calls onChange when the user types in the input", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <FarmSearchInput
        value=""
        onChange={onChange}
        onClear={vi.fn()}
        isLoading={false}
      />
    );
    // Typing a character should fire the onChange handler with the new value
    await user.type(screen.getByPlaceholderText(/search by farm id/i), "5");
    expect(onChange).toHaveBeenCalled();
  });

  it("calls onClear when the Clear button is clicked", async () => {
    const user = userEvent.setup();
    const onClear = vi.fn();
    render(
      <FarmSearchInput
        value="42"
        onChange={vi.fn()}
        onClear={onClear}
        isLoading={false}
      />
    );
    // Clicking Clear should invoke the clear callback to reset the query
    await user.click(screen.getByText("Clear"));
    expect(onClear).toHaveBeenCalledTimes(1);
  });

  it("does not call onChange when input is disabled during loading", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <FarmSearchInput
        value=""
        onChange={onChange}
        onClear={vi.fn()}
        isLoading={true}
      />
    );
    // A disabled input should not fire onChange even if the user attempts to type
    await user.type(screen.getByPlaceholderText(/search by farm id/i), "5");
    expect(onChange).not.toHaveBeenCalled();
  });
});

// FarmSearchPanel Interaction Tests
describe("FarmSearchPanel interactions", () => {
  const baseProps = {
    query: "",
    setQuery: vi.fn(),
    profile: null,
    isLoading: false,
    error: null,
    user: { name: "John" },
  };

  it("shows edit actions alongside a returned profile", async () => {
    // Admin role (set in beforeEach) means all action buttons should appear with a result
    render(
      <FarmSearchPanel {...baseProps} query="42" profile={mockProfile(42)} />
    );
    // Both the profile card and the Add action button should be visible together
    expect(screen.getByText("Farm #42")).toBeInTheDocument();
    expect(screen.getByText(/Add/i)).toBeInTheDocument();
  });

  it("calls setQuery when the user types in the search input", async () => {
    const user = userEvent.setup();
    const setQuery = vi.fn();
    render(<FarmSearchPanel {...baseProps} setQuery={setQuery} />);
    // Typing in the search input should propagate the new value via setQuery
    await user.type(screen.getByPlaceholderText(/search by farm id/i), "5");
    expect(setQuery).toHaveBeenCalled();
  });

  it("calls setQuery with empty string when Clear is clicked", async () => {
    const user = userEvent.setup();
    const setQuery = vi.fn();
    render(<FarmSearchPanel {...baseProps} query="42" setQuery={setQuery} />);
    // Clicking Clear should reset the query to an empty string
    await user.click(screen.getByText("Clear"));
    expect(setQuery).toHaveBeenCalledWith("");
  });
});
