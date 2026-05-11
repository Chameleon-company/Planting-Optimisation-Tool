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
import RegisterPage from "./pages/auth/RegisterPage";
import VerifyEmailPage from "./pages/auth/VerifyEmailPage";
import ForgotPasswordPage from "./pages/auth/ForgotPasswordPage";
import ResetPasswordPage from "./pages/auth/ResetPasswordPage";
import AdminLayout from "./components/layout/AdminLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminLogs from "./pages/admin/AdminLogs";
import RequireRole from "./components/auth/RequireRole";
import WeightingHub from "./pages/admin/settings/WeightingHub";
import AhpPage from "./pages/admin/settings/AhpPage";
import GlobalWeightsPage from "./pages/admin/settings/GlobalWeightsPage";
import AdminSpeciesPage from "./pages/admin/AdminSpeciesPage";
import FarmsManagementPage from "./pages/farmManagementPage";
import ScoringParametersPage from "./pages/admin/settings/ScoringParametersPage";
import ExclusionRulesPage from "./pages/admin/settings/ExclusionRulesPage";
import DependencyRulesPage from "./pages/admin/settings/DependencyRulesPage";
import AdminUsers from "./pages/admin/AdminUsers";

// Export App
export default function App() {
  return (
    <GlobalErrorBoundary>
      <Providers>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route element={<MainLayout />}>
              <Route path="/" index element={<HomePage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route
                path="/farms"
                element={
                  <RequireRole allowedRoles={["admin", "supervisor"]}>
                    <FarmsManagementPage />
                  </RequireRole>
                }
              />
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
              <Route path="species" element={<AdminSpeciesPage />} />
              <Route path="settings">
                <Route path="weighting">
                  {/* The intermediate menu */}
                  <Route index element={<WeightingHub />} />{" "}
                  {/* The standard AHP tool */}
                  <Route path="ahp" element={<AhpPage />} />{" "}
                  {/* The global weights*/}
                  <Route path="global" element={<GlobalWeightsPage />} />{" "}
                </Route>
                <Route path="scoring" element={<ScoringParametersPage />} />
                <Route path="exclusions" element={<ExclusionRulesPage />} />
                <Route path="dependencies" element={<DependencyRulesPage />} />
              </Route>
              <Route path="logs" element={<AdminLogs />} />
              <Route path="users" element={<AdminUsers />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </Providers>
    </GlobalErrorBoundary>
  );
}
