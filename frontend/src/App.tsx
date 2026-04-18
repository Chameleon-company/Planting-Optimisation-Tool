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
import WeightingHub from "./pages/admin/settings/WeightingHub";
import AhpPage from "./pages/admin/settings/AhpPage";
import HybridAhpPage from "./pages/admin/settings/HybridAhpPage";

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
              <Route path="settings">
                <Route index element={<AdminSettings />} /> {/* The Hub Page */}
                <Route path="weighting">
                  <Route index element={<WeightingHub />} />{" "}
                  {/* The intermediate menu */}
                  <Route path="ahp" element={<AhpPage />} />{" "}
                  {/* The standard AHP tool */}
                  <Route path="hybrid" element={<HybridAhpPage />} />{" "}
                  {/* The ML tool */}
                </Route>
              </Route>
              <Route path="logs" element={<AdminLogs />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </Providers>
    </GlobalErrorBoundary>
  );
}
