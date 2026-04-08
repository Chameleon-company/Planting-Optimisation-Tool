// @vitest-environment jsdom

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";

// Page
import SpeciesPage from "../pages/SpeciesPage";

// Mock hook
vi.mock("../hooks/useSpecies", () => ({
  useSpecies: vi.fn(),
}));

import { useSpecies } from "../hooks/useSpecies";
import { Species } from "../utils/contentfulClient";

describe("SpeciesPage", () => {
  it("renders species list when data is available", () => {
    vi.mocked(useSpecies).mockReturnValue({
      species: [
        {
          sys: { id: "1" },
          fields: {
            name: "Test Tree",
            description: { content: [] },
          },
        },
      ],
      isLoading: false, //
      error: null,
    });

    render(
      <BrowserRouter>
        <SpeciesPage />
      </BrowserRouter>
    );

    expect(screen.getByText("Test Tree")).toBeInTheDocument();
  });

  it("shows loading indicator while search is in progress", () => {
    vi.mocked(useSpecies).mockReturnValue({
      species: [],
      isLoading: true,
      error: null,
    });

    render(
      <BrowserRouter>
        <SpeciesPage />
      </BrowserRouter>
    );

    expect(screen.getByText("...")).toBeInTheDocument();
  });

  it("transitions from loading state to showing results", () => {
    // Start in loading state
    let state = {
      species: [] as Species[],
      isLoading: true,
      error: null,
    };

    vi.mocked(useSpecies).mockImplementation(() => state);

    const { rerender } = render(
      <BrowserRouter>
        <SpeciesPage />
      </BrowserRouter>
    );

    // Expect loading indicator to be present initially
    expect(screen.getByText("...")).toBeInTheDocument();

    // Simulate API response completing
    state = {
      species: [
        {
          sys: { id: "1" },
          fields: { name: "Teak", description: { content: [] } },
        },
      ],
      isLoading: false,
      error: null,
    };

    // Re-render with new state
    rerender(
      <BrowserRouter>
        <SpeciesPage />
      </BrowserRouter>
    );

    // Expect results to now be visible
    expect(screen.getByText("Teak")).toBeInTheDocument();
  });

  it("shows error message", () => {
    vi.mocked(useSpecies).mockReturnValue({
      species: [],
      isLoading: false,
      error: "Something went wrong",
    });

    render(
      <BrowserRouter>
        <SpeciesPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });

  it("shows empty state when no species found", () => {
    vi.mocked(useSpecies).mockReturnValue({
      species: [],
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <SpeciesPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/no species/i)).toBeInTheDocument();
  });
});
