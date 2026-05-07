// @vitest-environment jsdom
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";

// Page to test
import FarmsManagmentPage from "../pages/farmManagementPage";

// Mock farm shape
const mockFarm = (id: number) => ({
  id,
  rainfall_mm: 1200,
  temperature_celsius: 22,
  elevation_m: 300,
  ph: 6.5,
  soil_texture: { name: "Loam" },
  area_ha: 10.5,
  latitude: -37.81234,
  longitude: 144.96345,
  coastal: false,
  riparian: false,
  nitrogen_fixing: true,
  shade_tolerant: false,
  bank_stabilising: false,
  slope: 5.25,
  agroforestry_type: [{ id: 1, type_name: "Block" }],
});

// Mock hooks and context
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    user: { name: "Test Admin", role: "admin" },
    getAccessToken: () => "fake-token",
  }),
}));

vi.mock("@/hooks/useUserProfiles", () => ({
  useUserProfiles: () => ({
    farms: [mockFarm(1)],
    isLoading: false,
    error: null,
    page: 0,
    setPage: vi.fn(),
    totalFarms: 1,
    totalPages: 1,
    refetch: vi.fn(),
  }),
}));

vi.mock("@/hooks/useFarms", () => ({
  useFarms: () => ({
    isLoading: false,
    error: null,
    createFarm: vi.fn(),
    updateFarm: vi.fn(),
    deleteFarm: vi.fn(),
  }),
}));

vi.mock("react-helmet-async", () => ({
  Helmet: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

describe("FarmsManagmentPage", () => {
  it("renders the page title", () => {
    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );
    expect(screen.getByText("Farm Management")).toBeInTheDocument();
  });

  it("renders the farm count badge with the correct number", () => {
    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );
    expect(screen.getByText("1 farm")).toBeInTheDocument();
  });

  it("renders the action buttons for an admin user", () => {
    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );
    expect(screen.getByText(/register/i)).toBeInTheDocument();
    expect(screen.getByText(/edit/i)).toBeInTheDocument();
    expect(screen.getByText(/delete/i)).toBeInTheDocument();
  });

  it("renders the farms table with the mock farm", () => {
    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );
    expect(screen.getByText("Farm #1")).toBeInTheDocument();
    expect(screen.getByText("10.5 ha")).toBeInTheDocument();
  });

  it("does not show the register or edit modal on first render", () => {
    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );
    expect(
      screen.queryByRole("heading", { name: /register farm/i })
    ).not.toBeInTheDocument();
    expect(screen.queryByText(/edit farm/i)).not.toBeInTheDocument();
  });

  it("opens the register modal when Register button is clicked", async () => {
    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );
    await userEvent.click(screen.getByText(/register/i));
    expect(
      screen.getByRole("heading", { name: /register farm/i })
    ).toBeInTheDocument();
  });

  it("closes the register modal when Cancel is clicked", async () => {
    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );
    await userEvent.click(screen.getByText(/register/i));
    expect(
      screen.getByRole("heading", { name: /register farm/i })
    ).toBeInTheDocument();

    await userEvent.click(screen.getByText("Cancel"));
    expect(
      screen.queryByRole("heading", { name: /register farm/i })
    ).not.toBeInTheDocument();
  });

  it("opens the edit modal when a farm is selected and Edit is clicked", async () => {
    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );
    const checkbox = screen.getByRole("checkbox");
    await userEvent.click(checkbox);
    await userEvent.click(screen.getByText(/edit/i));

    expect(screen.getByText(/edit farm #1/i)).toBeInTheDocument();
  });

  it("closes the edit modal when Cancel is clicked", async () => {
    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );
    const checkbox = screen.getByRole("checkbox");
    await userEvent.click(checkbox);
    await userEvent.click(screen.getByText(/edit/i));
    expect(screen.getByText(/edit farm #1/i)).toBeInTheDocument();

    await userEvent.click(screen.getByText("Cancel"));
    expect(screen.queryByText(/edit farm #1/i)).not.toBeInTheDocument();
  });
});
