import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import RecommendationSkeleton from "@/components/recommendations/recommendationSkeleton";

describe("RecommendationSkeleton", () => {
  it("renders the recommendation loading skeleton", () => {
    render(<RecommendationSkeleton />);

    expect(screen.getByRole("status")).toBeInTheDocument();
  });
});
