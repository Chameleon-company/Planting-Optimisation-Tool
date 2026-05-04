import { render, screen } from "@testing-library/react";
import { HelmetProvider } from "react-helmet-async";
import DependencyRulesPage from "@/pages/admin/settings/DependencyRulesPage";

test("renders dependency rules placeholder", () => {
  render(
    <HelmetProvider>
      <DependencyRulesPage />
    </HelmetProvider>
  );

  // Check for the main heading[cite: 6]
  expect(
    screen.getByRole("heading", { name: /Dependency Rules/i })
  ).toBeInTheDocument();

  // Check for the placeholder text[cite: 6]
  expect(
    screen.getByText(
      /UI for managing species dependency rules is currently not implemented/i
    )
  ).toBeInTheDocument();
});
