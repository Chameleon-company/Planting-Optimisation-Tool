// @vitest-environment jsdom
import { describe, it, expect, vi } from "vitest";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

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

// Mock authentication context with a logged-in user
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    user: { name: "John", role: "admin" },
    getAccessToken: () => "fake-token",
  }),
}));

// ProfilePage Snapshot Tests
describe("ProfilePage Snapshot", () => {
  it("matches snapshot", () => {
    const { container } = render(
      <MemoryRouter>
        <ProfilePage />
      </MemoryRouter>
    );
    // Snapshot captures the full rendered output
    expect(container).toMatchSnapshot();
  });
});
