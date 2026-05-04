import { render, screen } from "@testing-library/react";
import { HelmetProvider } from "react-helmet-async";
import ScoringParametersPage from "@/pages/admin/settings/ScoringParametersPage";

test("renders scoring parameters placeholder", () => {
  render(
    <HelmetProvider>
      <ScoringParametersPage />
    </HelmetProvider>
  );

  // Check for the main heading[cite: 8]
  expect(
    screen.getByRole("heading", { name: /Scoring Parameters/i })
  ).toBeInTheDocument();

  // Check for the placeholder text[cite: 8]
  expect(
    screen.getByText(
      /UI for managing scoring parameters is currently not implemented/i
    )
  ).toBeInTheDocument();
});
