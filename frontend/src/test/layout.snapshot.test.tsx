// @vitest-environment jsdom

import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import Layout from "../components/layout/layout";

// Mock the custom hooks your layout now relies on
vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: null, // Capturing the default logged-out state
    logout: vi.fn(),
    login: vi.fn(),
    isLoading: false,
  }),
}));

describe("Layout Snapshot", () => {
  it("matches snapshot", () => {
    const { container } = render(
      <MemoryRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<div>Home</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    // Snapshot ensures layout structure doesn't change unexpectedly
    expect(container).toMatchSnapshot();
  });
});
