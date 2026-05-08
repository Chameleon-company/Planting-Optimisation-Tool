import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import WeightingHub from "@/pages/admin/settings/WeightingHub";
test("renders weighting hub and its navigation cards", () => {
  render(
    <HelmetProvider>
      <MemoryRouter>
        <WeightingHub />
      </MemoryRouter>
    </HelmetProvider>
  );

  // Check for the back button
  expect(
    screen.getByRole("link", { name: /← Back to Dashboard/i })
  ).toBeInTheDocument();

  // Check for the main page heading
  expect(
    screen.getByRole("heading", { name: "Weighting Methods" })
  ).toBeInTheDocument();

  // Check for the navigation cards
  expect(
    screen.getByRole("heading", { name: /Traditional AHP/i })
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /Global Weights/i })
  ).toBeInTheDocument();

  // Check if the card descriptions are present
  expect(
    screen.getByText(
      /Expert-driven pairwise comparison matrix and Eigenvector weighting./i
    )
  ).toBeInTheDocument();
  expect(
    screen.getByText(/Global weights derived from historical growth data./i)
  ).toBeInTheDocument();
});
