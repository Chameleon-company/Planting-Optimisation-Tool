// @vitest-environment jsdom
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { HelmetProvider } from "react-helmet-async";
import UserEvent from "@testing-library/user-event";

import RecommendationPage from "@/pages/RecommendationPage";

// Mock the custom hook
vi.mock("@/hooks/useRecommendations", () => ({
  useRecommendations: vi.fn(),
}));

import { useRecommendations } from "@/hooks/useRecommendations";

describe("RecommendationPage Integration", () => {
  it("does not show tables before a search has been performed", () => {
    vi.mocked(useRecommendations).mockReturnValue({
      recs: [],
      excludes: [],
      isLoading: false,
      hasSearched: false,
      error: null,
    });

    render(
      <HelmetProvider>
        <RecommendationPage />
      </HelmetProvider>
    );

    expect(
      screen.getByText(/Agroforestry Recommendations/i)
    ).toBeInTheDocument();
    // Tables should not be present yet
    expect(screen.queryByText("Top Fit Species")).not.toBeInTheDocument();
  });

  it("splits data into Top Fit and Cautionary tables based on score", () => {
    vi.mocked(useRecommendations).mockReturnValue({
      recs: [
        {
          species_id: 1,
          score_mcda: 0.85,
          rank_overall: 1,
          species_common_name: "Top Tree",
          species_name: "",
          key_reasons: [],
        },
        {
          species_id: 2,
          score_mcda: 0.6,
          rank_overall: 2,
          species_common_name: "Cautious Tree",
          species_name: "",
          key_reasons: [],
        },
      ],
      excludes: [],
      isLoading: false,
      hasSearched: true,
      error: null,
    });

    render(
      <HelmetProvider>
        <RecommendationPage />
      </HelmetProvider>
    );

    // Get the heading, then step up to its parent wrapper, and then up to the main card container
    const topFitHeading = screen.getByRole("heading", {
      name: "Top Fit Species",
    });
    const topFitSection = topFitHeading.parentElement?.parentElement;

    expect(topFitSection).toHaveTextContent("Top Tree");
    expect(topFitSection).not.toHaveTextContent("Cautious Tree");

    // Do the same for the Cautionary table
    const cautHeading = screen.getByRole("heading", {
      name: "Cautionary Species",
    });
    const cautSection = cautHeading.parentElement?.parentElement;

    expect(cautSection).toHaveTextContent("Cautious Tree");
  });

  it("updates search state when user interacts with input", async () => {
    const user = UserEvent.setup();

    vi.mocked(useRecommendations).mockReturnValue({
      recs: [],
      excludes: [],
      isLoading: false,
      hasSearched: false,
      error: null,
    });

    render(
      <HelmetProvider>
        <RecommendationPage />
      </HelmetProvider>
    );

    const input = screen.getByRole("spinbutton");
    await user.type(input, "99");

    expect(input).toHaveValue(99);
  });
});
