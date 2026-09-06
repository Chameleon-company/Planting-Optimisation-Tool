// @vitest-environment jsdom
import { beforeEach, describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";

// Page to test
import FarmsManagmentPage from "../pages/farmManagementPage";

const mocks = vi.hoisted(() => ({
  createFarm: vi.fn(),
  updateFarm: vi.fn(),
  deleteFarm: vi.fn(),
  refetch: vi.fn(),
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
  soilTextures: [
    {
      id: 1,
      name: "Loam",
    },
  ],
}));

vi.mock("react-hot-toast", () => ({
  default: {
    success: mocks.toastSuccess,
    error: mocks.toastError,
  },
}));

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
    refetch: mocks.refetch,
  }),
}));

vi.mock("@/hooks/useFarms", () => ({
  useFarms: () => ({
    isLoading: false,
    error: null,
    createFarm: mocks.createFarm,
    updateFarm: mocks.updateFarm,
    deleteFarm: mocks.deleteFarm,
  }),
}));

vi.mock("@/hooks/useSoilTextures", () => ({
  useSoilTextures: () => ({
    soilTextures: mocks.soilTextures,
    isLoading: false,
    error: null,
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
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.createFarm.mockResolvedValue(true);
    mocks.updateFarm.mockResolvedValue(true);
    mocks.deleteFarm.mockResolvedValue(true);
    mocks.refetch.mockResolvedValue(undefined);
  });
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

  it("shows success toast when a farm is created successfully", async () => {
    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );

    await user.click(screen.getByText(/register/i));

    // Fill the required form fields
    await user.type(screen.getByLabelText(/rainfall/i), "1200");
    await user.type(screen.getByLabelText(/temperature/i), "22");
    await user.type(screen.getByLabelText(/elevation/i), "300");
    await user.type(screen.getByLabelText(/soil pH/i), "6.5");
    await user.type(screen.getByLabelText(/area/i), "10.5");
    await user.type(screen.getByLabelText(/latitude/i), "-37.8");
    await user.type(screen.getByLabelText(/longitude/i), "144.9");
    await user.type(screen.getByLabelText(/slope/i), "5");

    await user.selectOptions(screen.getByLabelText(/soil texture/i), "1");

    await user.click(screen.getByRole("button", { name: /^block$/i }));

    await user.click(screen.getByRole("button", { name: /register farm/i }));

    await waitFor(() => {
      expect(mocks.createFarm).toHaveBeenCalled();
      expect(mocks.toastSuccess).toHaveBeenCalledWith(
        "Farm created successfully"
      );
    });
  });

  it("shows error toast when creating a farm fails", async () => {
    mocks.createFarm.mockResolvedValue(false);

    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );

    await user.click(screen.getByText(/register/i));

    await user.type(screen.getByLabelText(/rainfall/i), "1200");
    await user.type(screen.getByLabelText(/temperature/i), "22");
    await user.type(screen.getByLabelText(/elevation/i), "300");
    await user.type(screen.getByLabelText(/soil pH/i), "6.5");
    await user.type(screen.getByLabelText(/area/i), "10.5");
    await user.type(screen.getByLabelText(/latitude/i), "-37.8");
    await user.type(screen.getByLabelText(/longitude/i), "144.9");
    await user.type(screen.getByLabelText(/slope/i), "5");

    await user.selectOptions(screen.getByLabelText(/soil texture/i), "1");

    await user.click(screen.getByRole("button", { name: /^block$/i }));

    await user.click(screen.getByRole("button", { name: /register farm/i }));

    await waitFor(() => {
      expect(mocks.toastError).toHaveBeenCalledWith("Failed to create farm");
    });
  });

  it("shows success toast when a farm is updated successfully", async () => {
    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );

    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByText(/edit/i));

    await user.selectOptions(screen.getByLabelText(/soil texture/i), "1");

    await user.click(screen.getByRole("button", { name: /save changes/i }));

    await waitFor(() => {
      expect(mocks.updateFarm).toHaveBeenCalled();
      expect(mocks.toastSuccess).toHaveBeenCalledWith(
        "Farm updated successfully"
      );
    });
  });

  it("shows error toast when updating a farm fails", async () => {
    mocks.updateFarm.mockResolvedValue(false);

    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );

    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByText(/edit/i));

    await user.selectOptions(screen.getByLabelText(/soil texture/i), "1");

    await user.click(screen.getByRole("button", { name: /save changes/i }));

    await waitFor(() => {
      expect(mocks.toastError).toHaveBeenCalledWith("Failed to update farm");
    });
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

  it("shows success toast when a farm is deleted successfully", async () => {
    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );

    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByText(/delete/i));

    await user.click(screen.getByRole("button", { name: /confirm delete/i }));

    expect(mocks.deleteFarm).toHaveBeenCalledWith(1);

    expect(mocks.toastSuccess).toHaveBeenCalledWith(
      "Farm deleted successfully"
    );
  });

  it("shows error toast when deleting a farm fails", async () => {
    mocks.deleteFarm.mockResolvedValue(false);

    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <FarmsManagmentPage />
      </BrowserRouter>
    );

    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByText(/delete/i));

    await user.click(screen.getByRole("button", { name: /confirm delete/i }));

    expect(mocks.deleteFarm).toHaveBeenCalledWith(1);

    expect(mocks.toastError).toHaveBeenCalledWith("Failed to delete farm");
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
