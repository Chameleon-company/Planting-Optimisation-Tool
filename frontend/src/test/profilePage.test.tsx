// @vitest-environment jsdom
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";

// Page to test
import ProfilePage from "../pages/ProfilePage";

// Mock Functions
vi.mock("../hooks/useUserProfiles", () => ({
  useUserProfiles: () => ({
    farms: [],
    isLoading: false,
    error: null,
    page: 0,
    setPage: vi.fn(),
    totalPages: 0,
    totalFarms: 0,
  }),
}));

vi.mock("../hooks/useSearchProfiles", () => ({
  useSearchProfiles: () => ({
    profile: null,
    isLoading: false,
    error: null,
  }),
}));

// Mock authentication with a logged-in user
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    user: { name: "John", role: "admin" },
    getAccessToken: () => "fake-token",
  }),
}));

// ProfilePage Tests
describe("ProfilePage", () => {
  it("renders the page title", () => {
    render(
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    );
    // The main Environmental Profile heading should always be present on the page
    expect(screen.getByText("Environmental Profile")).toBeInTheDocument();
  });

  it("renders the farmer name in the header", () => {
    render(
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    );
    // The header subtitle should show the authenticated user's name
    expect(screen.getByText(/John/i)).toBeInTheDocument();
  });

  it("renders the search input", () => {
    render(
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    );
    // The search panel's input should always be visible on the profile page
    expect(
      screen.getByPlaceholderText(/search by farm id/i)
    ).toBeInTheDocument();
  });

  it("renders the empty farms state when user has no farms", () => {
    render(
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    );
    // With no farms returned from the hook the empty state message should appear
    expect(screen.getByText(/no farms found/i)).toBeInTheDocument();
  });
});
