// Import wrappers for the main Pages
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Providers } from "./contexts/Providers";
import GlobalErrorBoundary from "./errors/GlobalErrorBoundary";

// Import Pages
import MainLayout from "./components/layout/layout";
import HomePage from "./pages/HomePage";
import ProfilePage from "./pages/ProfilePage";
import CalculatorPage from "./pages/CalculatorPage";
import RecommendationPage from "./pages/RecommendationPage";
import SpeciesPage from "./pages/SpeciesPage";
import NotFoundPage from "./pages/NotFoundPage";
import LoginPage from "./pages/auth/LoginPage";
import AdminLayout from "./components/layout/AdminLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminSettings from "./pages/admin/AdminSettings";
import AdminLogs from "./pages/admin/AdminLogs";
import RequireRole from "./components/auth/RequireRole";

// Export App
export default function App() {
  return (
    <GlobalErrorBoundary>
      <Providers>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<MainLayout />}>
              <Route path="/" index element={<HomePage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/calculator" element={<CalculatorPage />} />
              <Route path="/recommendation" element={<RecommendationPage />} />
              <Route path="/species" element={<SpeciesPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>

            <Route
              path="/admin"
              element={
                <RequireRole allowedRoles={["admin"]}>
                  <AdminLayout />
                </RequireRole>
              }
            >
              <Route index element={<AdminDashboard />} />
              <Route path="settings" element={<AdminSettings />} />
              <Route path="logs" element={<AdminLogs />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </Providers>
    </GlobalErrorBoundary>
  );
}
