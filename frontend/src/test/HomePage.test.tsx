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
      screen.getByText(/Generate environmental profile/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/Bulk Sapling Calculator/i)).toBeInTheDocument();
    expect(screen.getByText(/Species Information/i)).toBeInTheDocument();
  });
});
