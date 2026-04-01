// @vitest-environment jsdom

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";

import SpeciesPage from "../pages/SpeciesPage";

// Mock hook - only mock once
vi.mock("../hooks/useSpecies", () => ({
  useSpecies: vi.fn(),
}));

import { useSpecies } from "../hooks/useSpecies";

describe("SpeciesPage Interactions", () => {
  describe("Species search interaction", () => {
    it("filters species based on search input", async () => {
      const user = userEvent.setup();

      vi.mocked(useSpecies).mockReturnValue({
        species: [
          {
            sys: { id: "1" },
            fields: { name: "Teak", description: { content: [] } },
          },
          {
            sys: { id: "2" },
            fields: { name: "Mahogany", description: { content: [] } },
          },
        ],
        isLoading: false,
        error: null,
      });

      render(
        <BrowserRouter>
          <SpeciesPage />
        </BrowserRouter>
      );

      const input = screen.getByPlaceholderText(/enter keywords/i);

      await user.type(input, "Teak");
      await user.keyboard("{Enter}");

      // Expect filtered result
      expect(vi.mocked(useSpecies)).toHaveBeenCalledWith("Teak");
    });
  });

  describe("Species modal interaction", () => {
    it("opens modal correctly when View Details is clicked", async () => {
      const user = userEvent.setup();

      vi.mocked(useSpecies).mockReturnValue({
        species: [
          {
            sys: { id: "1" },
            fields: { name: "Teak", description: { content: [] } },
          },
        ],
        isLoading: false,
        error: null,
      });

      render(
        <BrowserRouter>
          <SpeciesPage />
        </BrowserRouter>
      );

      // Click "View Details"
      const button = screen.getByText(/view details/i);
      await user.click(button);

      // Modal should appear with active class
      expect(document.querySelector(".side-modal.active")).toBeInTheDocument();
    });

    it("closes modal when close button is clicked", async () => {
      const user = userEvent.setup();

      vi.mocked(useSpecies).mockReturnValue({
        species: [
          {
            sys: { id: "1" },
            fields: { name: "Teak", description: { content: [] } },
          },
        ],
        isLoading: false,
        error: null,
      });

      render(
        <BrowserRouter>
          <SpeciesPage />
        </BrowserRouter>
      );

      // Open modal
      await user.click(screen.getByText(/view details/i));
      expect(document.querySelector(".side-modal.active")).toBeInTheDocument();

      // Close modal using X button
      const closeBtn = screen.getByRole("button", { name: /×/i });
      await user.click(closeBtn);

      // Modal should be gone after closing
      expect(
        document.querySelector(".side-modal.active")
      ).not.toBeInTheDocument();
    });
  });

  it("triggers search on Enter key press", async () => {
    const user = userEvent.setup();

    vi.mocked(useSpecies).mockReturnValue({
      species: [
        {
          sys: { id: "1" },
          fields: { name: "Teak", description: { content: [] } },
        },
      ],
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <SpeciesPage />
      </BrowserRouter>
    );

    const input = screen.getByPlaceholderText(/enter keywords/i);
    await user.type(input, "Teak{enter}");

    expect(screen.getByText("Teak")).toBeInTheDocument();
  });

  it("handles empty search input gracefully", async () => {
    const user = userEvent.setup();

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

    const input = screen.getByPlaceholderText(/enter keywords/i);

    // User presses enter without typing anything
    await user.type(input, "{enter}");

    // Should not crash and should show empty state
    expect(screen.getByText(/no species/i)).toBeInTheDocument();
  });

  it("handles very long search input", async () => {
    const longText = "a".repeat(500);

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

    const input = screen.getByPlaceholderText(/enter keywords/i);
    fireEvent.change(input, { target: { value: longText } });

    // Ensure app still works
    expect(input).toHaveValue(longText);
  });

  it("handles special characters in search input", async () => {
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

    const input = screen.getByPlaceholderText(/enter keywords/i);
    fireEvent.change(input, { target: { value: "@#$%^&*" } });

    expect(input).toHaveValue("@#$%^&*");
  });

  it("shows empty state when no results and no error", () => {
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

    // Important distinction: not error, just empty
    expect(screen.getByText(/no species/i)).toBeInTheDocument();
  });

  it("handles rapid typing without crashing", async () => {
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

    const input = screen.getByPlaceholderText(/enter keywords/i);

    // Simulate fast typing
    fireEvent.change(input, { target: { value: "teak mahogany eucalyptus" } });

    expect(input).toHaveValue("teak mahogany eucalyptus");
  });

  it("handles species with missing description", async () => {
    const user = userEvent.setup();

    vi.mocked(useSpecies).mockReturnValue({
      species: [
        {
          sys: { id: "1" },
          fields: { name: "Test Tree", description: { content: [] } },
        },
      ],
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <SpeciesPage />
      </BrowserRouter>
    );

    await user.click(screen.getByText(/view details/i));

    // Should not crash and still render modal
    expect(document.querySelector(".side-modal.active")).toBeInTheDocument();
  });

  it("does not crash when closing modal multiple times", async () => {
    const user = userEvent.setup();

    vi.mocked(useSpecies).mockReturnValue({
      species: [
        {
          sys: { id: "1" },
          fields: { name: "Test Tree", description: { content: [] } },
        },
      ],
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <SpeciesPage />
      </BrowserRouter>
    );

    await user.click(screen.getByText(/view details/i));

    const closeBtn = screen.getByRole("button", { name: /×/i });
    await user.click(closeBtn);

    // Try closing again (edge case) and ensure it does not reject
    await expect(user.click(closeBtn)).resolves.toBeUndefined();
  });
});
