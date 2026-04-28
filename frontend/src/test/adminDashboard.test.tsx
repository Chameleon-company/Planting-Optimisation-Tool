import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import AdminDashboard from "@/pages/admin/AdminDashboard";

test("renders dashboard and species link", () => {
  render(
    <MemoryRouter>
      <AdminDashboard />
    </MemoryRouter>
  );

  expect(screen.getByText(/Dashboard Overview/i)).toBeInTheDocument();
  expect(screen.getByText(/Species Management/i)).toBeInTheDocument();
});
