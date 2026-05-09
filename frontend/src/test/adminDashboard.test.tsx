import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import AdminDashboard from "@/pages/admin/AdminDashboard";

test("renders admin dashboard with management and settings sections", () => {
  render(
    <HelmetProvider>
      <MemoryRouter>
        <AdminDashboard />
      </MemoryRouter>
    </HelmetProvider>
  );

  // Check for the main section headings
  expect(
    screen.getByRole("heading", { name: /Management Operations/i })
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /Scoring Settings/i })
  ).toBeInTheDocument();

  // Check for the specific navigation card titles using getByRole
  expect(
    screen.getByRole("heading", { name: /Species Management/i })
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /User Management/i })
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /Weighting Methods/i })
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /Scoring Parameters/i })
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /Exclusion Rules/i })
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /Dependency Rules/i })
  ).toBeInTheDocument();
});
