import { render, screen } from "@testing-library/react";
import { HelmetProvider } from "react-helmet-async";
import ExclusionRulesPage from "@/pages/admin/settings/ExclusionRulesPage";

test("renders exclusion rules placeholder", () => {
  render(
    <HelmetProvider>
      <ExclusionRulesPage />
    </HelmetProvider>
  );

  // Check for the main heading[cite: 7]
  expect(
    screen.getByRole("heading", { name: /Exclusion Rules/i })
  ).toBeInTheDocument();

  // Check for the placeholder text[cite: 7]
  expect(
    screen.getByText(
      /UI for managing species exclusion rules is currently not implemented/i
    )
  ).toBeInTheDocument();
});
