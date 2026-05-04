// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Farm } from "@/hooks/useUserProfiles";

import EditFarmModal from "@/components/farmManagement/farnEditModal";
import FarmManageActions from "@/components/farmManagement/farmManagementEditButtons";
import FarmsTable from "@/components/farmManagement/farmsTable";
import RegisterFarmModal from "@/components/farmManagement/farmRegisterModal";

// Shared mock data
const mockFarm = (id: number): Farm => ({
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
  agroforestry_type: [{ name: "Block" }],
});

// Mock Functions

const mockUseAuth = vi.fn();
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
}));

beforeEach(() => {
  // Default to an admin user so all action buttons are visible unless overridden
  mockUseAuth.mockReturnValue({
    user: { name: "Test Admin", role: "admin" },
    getAccessToken: () => "mock-token",
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

// FarmManageActions interactions Tests
describe("FarmManageActions interactions", () => {
  it("fires the onAdd callback when Register is clicked", async () => {
    const user = userEvent.setup();
    const onAdd = vi.fn();
    mockUseAuth.mockReturnValue({ user: { name: "Admin", role: "admin" } });
    render(<FarmManageActions onAdd={onAdd} />);
    await user.click(screen.getByText(/register/i));
    expect(onAdd).toHaveBeenCalledTimes(1);
  });

  it("fires the onEdit callback when Edit is clicked", async () => {
    const user = userEvent.setup();
    const onEdit = vi.fn();
    mockUseAuth.mockReturnValue({ user: { name: "Admin", role: "admin" } });
    render(<FarmManageActions onEdit={onEdit} />);
    await user.click(screen.getByText(/edit/i));
    expect(onEdit).toHaveBeenCalledTimes(1);
  });

  it("fires the onDelete callback when Delete is clicked", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    mockUseAuth.mockReturnValue({ user: { name: "Admin", role: "admin" } });
    render(<FarmManageActions onDelete={onDelete} />);
    await user.click(screen.getByText(/delete/i));
    expect(onDelete).toHaveBeenCalledTimes(1);
  });
});

// FarmsTable interactions Tests
describe("FarmsTable interactions", () => {
  const baseProps = {
    farms: [],
    isLoading: false,
    user: { name: "Admin", role: "admin" },
    page: 0,
    totalPages: 1,
    setPage: vi.fn(),
    selectedFarmId: null,
    onSelectFarm: vi.fn(),
  };

  it("navigates to the farm dashboard when a row is clicked", async () => {
    const user = userEvent.setup();
    render(<FarmsTable {...baseProps} farms={[mockFarm(7)]} />);
    await user.click(screen.getByText("Farm #7"));
    // Clicking a row should push the farm's detail route
    expect(mockNavigate).toHaveBeenCalledWith("/profile?farmId=7");
  });

  it("calls onSelectFarm with the farm id when the checkbox is clicked", async () => {
    const user = userEvent.setup();
    const onSelectFarm = vi.fn();
    render(
      <FarmsTable
        {...baseProps}
        farms={[mockFarm(3)]}
        onSelectFarm={onSelectFarm}
      />
    );
    // The checkbox span sits inside the row — click it without triggering navigation
    const checkbox = screen.getByRole("checkbox");
    await user.click(checkbox);
    expect(onSelectFarm).toHaveBeenCalledWith(3);
  });

  it("deselects a farm when its already-selected checkbox is clicked", async () => {
    const user = userEvent.setup();
    const onSelectFarm = vi.fn();
    render(
      <FarmsTable
        {...baseProps}
        farms={[mockFarm(3)]}
        selectedFarmId={3}
        onSelectFarm={onSelectFarm}
      />
    );
    // Clicking the active checkbox should pass null back to clear the selection
    const checkbox = screen.getByRole("checkbox");
    await user.click(checkbox);
    expect(onSelectFarm).toHaveBeenCalledWith(null);
  });
});

// RegisterFarmModal interactions Tests
describe("RegisterFarmModal interactions", () => {
  it("calls onClose when the close button is clicked", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<RegisterFarmModal onClose={onClose} onSuccess={vi.fn()} />);
    await user.click(screen.getByText("✕"));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when Escape key is pressed", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<RegisterFarmModal onClose={onClose} onSuccess={vi.fn()} />);
    await user.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when the overlay backdrop is clicked", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<RegisterFarmModal onClose={onClose} onSuccess={vi.fn()} />);
    // Click the overlay element itself, not the modal card inside it
    const overlay = document.querySelector(
      ".farms-modal-overlay"
    ) as HTMLElement;
    await user.click(overlay);
    expect(onClose).toHaveBeenCalled();
  });

  it("calls onClose when Cancel is clicked", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<RegisterFarmModal onClose={onClose} onSuccess={vi.fn()} />);
    await user.click(screen.getByText("Cancel"));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("shows validation errors when submitted with empty required fields", async () => {
    const user = userEvent.setup();
    render(<RegisterFarmModal onClose={vi.fn()} onSuccess={vi.fn()} />);

    const registerButton = screen.getByRole("button", {
      name: "Register farm",
    });
    await user.click(registerButton);

    // At least one validation error message should appear without calling onSuccess
    const errorMessages = await screen.findAllByText(/required/i);
    expect(errorMessages.length).toBeGreaterThan(0);
  });
});

// EditFarmModal interactions Tests
describe("EditFarmModal interactions", () => {
  const farm = mockFarm(5);

  it("calls onClose when the close button is clicked", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<EditFarmModal farm={farm} onClose={onClose} onSuccess={vi.fn()} />);
    await user.click(screen.getByText("✕"));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when Escape key is pressed", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<EditFarmModal farm={farm} onClose={onClose} onSuccess={vi.fn()} />);
    await user.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
