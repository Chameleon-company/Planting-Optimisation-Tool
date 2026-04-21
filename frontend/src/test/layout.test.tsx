import "@testing-library/jest-dom/vitest";
import { it, expect, describe, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";

import MainLayout from "../components/layout/layout";
import { useAuth } from "@/contexts/AuthContext";
import { useStickyHeader } from "@/hooks/useStickyHeader";

// Setup Mocks
const mockLogout = vi.fn();
const mockNavigate = vi.fn();

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/hooks/useStickyHeader", () => ({
  useStickyHeader: vi.fn(),
}));

vi.mock("react-router-dom", async () => {
  const actual =
    await vi.importActual<typeof import("react-router-dom")>(
      "react-router-dom"
    );
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Helper function to render the layout with a specific initial route
const renderWithRouter = (initialPath = "/") => {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="*" element={<div>Page Content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
};

describe("MainLayout", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default mock states
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      logout: mockLogout,
      login: vi.fn(),
      isLoading: false,
      getAccessToken: vi.fn(() => null),
    });

    vi.mocked(useStickyHeader).mockReturnValue({ isScrolled: false });
  });

  it("renders the navigation and footer components", () => {
    const { container } = renderWithRouter();

    expect(container.querySelector(".topbar")).toBeInTheDocument();
    expect(container.querySelector(".site-footer")).toBeInTheDocument();

    // Check for some main nav links
    // Use getAllByRole because these links appear in both the header AND the footer
    const homeLinks = screen.getAllByRole("link", { name: /home/i });
    expect(homeLinks).toHaveLength(2); // Expecting 2 identical links

    const calculatorLinks = screen.getAllByRole("link", {
      name: /sapling calculator/i,
    });
    expect(calculatorLinks).toHaveLength(2); // Expecting 2 identical links
  });

  it("applies the 'home-topbar' class only when on the root route", () => {
    // Render on Home page
    const { container: homeContainer, unmount } = renderWithRouter("/");
    expect(
      homeContainer.querySelector(".topbar.home-topbar")
    ).toBeInTheDocument();
    unmount();

    // Render on another page (e.g., /calculator)
    const { container: otherContainer } = renderWithRouter("/calculator");
    expect(
      otherContainer.querySelector(".topbar.home-topbar")
    ).not.toBeInTheDocument();
  });

  it("adds the 'is-scrolled' class when useStickyHeader returns true", () => {
    // Override the mock for this specific test
    vi.mocked(useStickyHeader).mockReturnValue({ isScrolled: true });

    const { container } = renderWithRouter();

    // Expect the topbar to have the is-scrolled class
    expect(container.querySelector(".topbar.is-scrolled")).toBeInTheDocument();
  });

  it("shows the Login link when the user is not authenticated", () => {
    renderWithRouter();

    expect(screen.getByRole("link", { name: /login/i })).toBeInTheDocument();
    expect(screen.queryByText(/welcome,/i)).not.toBeInTheDocument();
  });

  it("shows user info and logout button when authenticated", async () => {
    // Override auth mock to simulate a logged-in user
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 1,
        name: "Test User",
        role: "admin",
        email: "test@test.com",
        farms: [],
      },
      logout: mockLogout,
      login: vi.fn(),
      isLoading: false,
      getAccessToken: vi.fn(() => "test-token"),
    });

    renderWithRouter();

    expect(screen.getByText("Welcome, Test User")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /logout/i })).toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: /login/i })
    ).not.toBeInTheDocument();
  });

  it("calls logout and navigates to home when logout button is clicked", async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 1,
        name: "Test User",
        role: "admin",
        email: "test@test.com",
        farms: [],
      },
      logout: mockLogout,
      login: vi.fn(),
      isLoading: false,
      getAccessToken: vi.fn(() => "test-token"),
    });

    renderWithRouter();

    const logoutBtn = screen.getByRole("button", { name: /logout/i });
    await userEvent.click(logoutBtn);

    expect(mockLogout).toHaveBeenCalledOnce();
    expect(mockNavigate).toHaveBeenCalledWith("/");
  });
});
