// @vitest-environment jsdom

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";

// Page to test
import HomePage from "../pages/HomePage";

describe("HomePage", () => {
  it("renders homepage content correctly", () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );

    // Check key UI text exists
    expect(
      screen.getAllByText(/Agroforestry Recommendations/i).length
    ).toBeGreaterThan(0);
    expect(
      screen.getAllByText(/Sapling Estimation Calculator/i).length
    ).toBeGreaterThan(0);
    expect(screen.getAllByText(/Species Information/i).length).toBeGreaterThan(
      0
    );
  });
});
