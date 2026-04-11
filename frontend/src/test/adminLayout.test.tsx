import "@testing-library/jest-dom/vitest";
import { describe, expect, it } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import { HelmetProvider } from "react-helmet-async";

import AdminLayout from "../components/layout/AdminLayout";
import AdminDashboard from "../pages/admin/AdminDashboard";
import AdminSettings from "../pages/admin/AdminSettings";
import AdminLogs from "../pages/admin/AdminLogs";
import { AuthProvider } from "../contexts/AuthContext";

function renderAdminRoute(initialPath: string) {
  return render(
    <HelmetProvider>
      <AuthProvider>
        <MemoryRouter initialEntries={[initialPath]}>
          <Routes>
            <Route path="/admin" element={<AdminLayout />}>
              <Route index element={<AdminDashboard />} />
              <Route path="settings" element={<AdminSettings />} />
              <Route path="logs" element={<AdminLogs />} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    </HelmetProvider>
  );
}

describe("AdminLayout", () => {
  it("renders the admin shell and dashboard content", () => {
    renderAdminRoute("/admin");

    expect(screen.getByText("Management Panel")).toBeInTheDocument();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
    expect(screen.getByText("Audit Logs")).toBeInTheDocument();
    expect(screen.getByText("Dashboard Overview")).toBeInTheDocument();
  });

  it("renders the settings page inside the admin shell", () => {
    renderAdminRoute("/admin/settings");

    expect(screen.getByText("Management Panel")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Settings" })
    ).toBeInTheDocument();
    expect(
      screen.getByText(/support configuration controls/i)
    ).toBeInTheDocument();
  });

  it("renders the audit logs page inside the admin shell", () => {
    renderAdminRoute("/admin/logs");

    expect(screen.getByText("Management Panel")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Audit Logs" })
    ).toBeInTheDocument();
    expect(
      screen.getByText(/display system audit activity/i)
    ).toBeInTheDocument();
  });
});
