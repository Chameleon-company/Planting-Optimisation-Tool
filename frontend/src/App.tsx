// Import wrappers for the main Pages
import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Providers } from "./contexts/Providers";
import GlobalErrorBoundary from "./errors/GlobalErrorBoundary";

// Import Pages
import MainLayout from "./components/layout/layout";
import AdminLayout from "./components/layout/AdminLayout";
import RequireRole from "./components/auth/RequireRole";

const HomePage = lazy(() => import("./pages/HomePage"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));
const CalculatorPage = lazy(() => import("./pages/CalculatorPage"));
const RecommendationPage = lazy(() => import("./pages/RecommendationPage"));
const SpeciesPage = lazy(() => import("./pages/SpeciesPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));
const LoginPage = lazy(() => import("./pages/auth/LoginPage"));
const RegisterPage = lazy(() => import("./pages/auth/RegisterPage"));
const VerifyEmailPage = lazy(() => import("./pages/auth/VerifyEmailPage"));
const ForgotPasswordPage = lazy(
  () => import("./pages/auth/ForgotPasswordPage")
);
const ResetPasswordPage = lazy(() => import("./pages/auth/ResetPasswordPage"));
const AdminDashboard = lazy(() => import("./pages/admin/AdminDashboard"));
const AdminLogs = lazy(() => import("./pages/admin/AdminLogs"));
const AdminSpeciesPage = lazy(() => import("./pages/admin/AdminSpeciesPage"));
const AdminUsers = lazy(() => import("./pages/admin/AdminUsers"));
const WeightingHub = lazy(() => import("./pages/admin/settings/WeightingHub"));
const AhpPage = lazy(() => import("./pages/admin/settings/AhpPage"));
const GlobalWeightsPage = lazy(
  () => import("./pages/admin/settings/GlobalWeightsPage")
);
const ScoringParametersPage = lazy(
  () => import("./pages/admin/settings/ScoringParametersPage")
);
const ExclusionRulesPage = lazy(
  () => import("./pages/admin/settings/ExclusionRulesPage")
);
const DependencyRulesPage = lazy(
  () => import("./pages/admin/settings/DependencyRulesPage")
);
const CompatibilityMatrixPage = lazy(
  () => import("./pages/admin/settings/CompatibilityMatrixPage")
);
const FarmsManagementPage = lazy(() => import("./pages/farmManagementPage"));

// Export App
export default function App() {
  return (
    <GlobalErrorBoundary>
      <Providers>
        <BrowserRouter>
          <Suspense
            fallback={
              <div role="status" aria-live="polite">
                Loading page...
              </div>
            }
          >
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
                <Route
                  path="/recommendation"
                  element={<RecommendationPage />}
                />
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
                  <Route
                    path="dependencies"
                    element={<DependencyRulesPage />}
                  />
                  <Route
                    path="compatibility"
                    element={<CompatibilityMatrixPage />}
                  />
                </Route>
                <Route path="logs" element={<AdminLogs />} />
                <Route path="users" element={<AdminUsers />} />
              </Route>
            </Routes>
          </Suspense>
        </BrowserRouter>
      </Providers>
    </GlobalErrorBoundary>
  );
}
