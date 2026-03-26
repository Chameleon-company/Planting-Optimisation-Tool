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

// Export App
export default function App() {
  return (
    <GlobalErrorBoundary>
      <Providers>
        <BrowserRouter>
          <Routes>
            <Route element={<MainLayout />}>
              <Route path="/" index element={<HomePage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/calculator" element={<CalculatorPage />} />
              <Route path="/recommendation" element={<RecommendationPage />} />
              <Route path="/species" element={<SpeciesPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </Providers>
    </GlobalErrorBoundary>
  );
}
