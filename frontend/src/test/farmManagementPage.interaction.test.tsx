// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Farm } from "@/hooks/useUserProfiles";

import EditFarmModal from "@/components/farmManagement/farmsEditModal";
import FarmManageActions from "@/components/farmManagement/farmManagementEditButtons";
import FarmsTable from "@/components/farmManagement/farmsTable";
import RegisterFarmModal from "@/components/farmManagement/farmRegisterModal";
import RegisterFarmForm from "@/components/farmManagement/farmForms/farmRegisterForm";
import FarmEditForm from "@/components/farmManagement/farmForms/farmEditForm";

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
  agroforestry_type: [{ id: 1, type_name: "Block" }],
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

const mockSoilTextures = vi.fn();
vi.mock("@/hooks/useSoilTextures", () => ({
  useSoilTextures: () => mockSoilTextures(),
}));

const mockAgroforestryTypes = vi.fn();
vi.mock("@/hooks/useAgroforestryTypes", () => ({
  useAgroforestryTypes: () => mockAgroforestryTypes(),
}));

beforeEach(() => {
  // Default to an admin user so all action buttons are visible unless overridden
  mockUseAuth.mockReturnValue({
    user: { name: "Test Admin", role: "admin" },
    getAccessToken: () => "mock-token",
  });
  mockSoilTextures.mockReturnValue({
    soilTextures: [
      { id: 1, name: "Loam" },
      { id: 2, name: "Clay" },
    ],
    isLoading: false,
  });
  mockAgroforestryTypes.mockReturnValue({
    agroforestryTypes: [],
    isLoading: false,
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

// FarmManageActions interactions Tests
describe("FarmManageActions ", () => {
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

  it("fires the onDelete callback when Delete is confirmed in the modal", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    mockUseAuth.mockReturnValue({ user: { name: "Admin", role: "admin" } });
    render(<FarmManageActions onDelete={onDelete} />);
    await user.click(screen.getByText(/delete/i));
    expect(
      screen.getByText(/are you sure you want to delete this farm/i)
    ).toBeInTheDocument();
    await user.click(screen.getByText(/confirm delete/i));
    expect(onDelete).toHaveBeenCalledTimes(1);
  });
});

// FarmsTable interactions Tests
describe("FarmsTable ", () => {
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
describe("RegisterFarmModal ", () => {
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

describe("RegisterFarmForm", () => {
  const onCancel = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("updates a field value on change and clears the matching error", async () => {
    render(<RegisterFarmForm onCancel={onCancel} onSuccess={onSuccess} />);
    const registerBtn = screen.getByRole("button", { name: "Register farm" });
    await userEvent.click(registerBtn);
    expect(screen.getByText(/rainfall is required/i)).toBeInTheDocument();

    const rainfallInput = screen.getByLabelText(/rainfall/i);
    await userEvent.clear(rainfallInput);
    await userEvent.type(rainfallInput, "800");
    expect(screen.queryByText(/rainfall is required/i)).not.toBeInTheDocument();
    expect(rainfallInput).toHaveValue(800);
  });

  it("toggles boolean fields", async () => {
    render(<RegisterFarmForm onCancel={onCancel} onSuccess={onSuccess} />);
    const coastalBtn = screen.getByRole("button", { name: /Coastal/i });
    expect(coastalBtn).not.toHaveClass("register-farm-toggle-active");
    await userEvent.click(coastalBtn);
    expect(coastalBtn).toHaveClass("register-farm-toggle-active");
  });

  it("toggles agroforestry type toggles on and off", async () => {
    render(<RegisterFarmForm onCancel={onCancel} onSuccess={onSuccess} />);
    const blockBtn = screen.getByRole("button", { name: /Block/i });
    expect(blockBtn).not.toHaveClass("register-farm-toggle-active");
    await userEvent.click(blockBtn);
    expect(blockBtn).toHaveClass("register-farm-toggle-active");
    await userEvent.click(blockBtn);
    expect(blockBtn).not.toHaveClass("register-farm-toggle-active");
  });

  it("submits valid data and calls onSuccess with parsed payload", async () => {
    render(<RegisterFarmForm onCancel={onCancel} onSuccess={onSuccess} />);
    await userEvent.type(screen.getByLabelText(/rainfall/i), "800");
    await userEvent.type(screen.getByLabelText(/temperature/i), "22");
    await userEvent.type(screen.getByLabelText(/elevation/i), "150");
    await userEvent.type(screen.getByLabelText(/soil ph/i), "6.5");
    await userEvent.selectOptions(screen.getByLabelText(/soil texture/i), "1");
    await userEvent.type(screen.getByLabelText(/area/i), "5");
    await userEvent.type(screen.getByLabelText(/latitude/i), "-37.8");
    await userEvent.type(screen.getByLabelText(/longitude/i), "144.9");
    await userEvent.type(screen.getByLabelText(/slope/i), "3.2");

    await userEvent.click(screen.getByRole("button", { name: /Coastal/i }));

    await userEvent.click(screen.getByRole("button", { name: /Block/i }));

    await userEvent.click(
      screen.getByRole("button", { name: "Register farm" })
    );
    await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1));

    const payload = onSuccess.mock.calls[0][0];
    expect(payload.rainfall_mm).toBe(800);
    expect(payload.temperature_celsius).toBe(22);
    expect(payload.soil_texture_id).toBe(1);
    expect(payload.coastal).toBe(true);
    expect(payload.riparian).toBe(false);
    expect(payload.agroforestry_type_ids).toContain(1);
  });

  it("shows validation errors on empty submit and does not call onSuccess", async () => {
    render(<RegisterFarmForm onCancel={onCancel} onSuccess={onSuccess} />);
    await userEvent.click(
      screen.getByRole("button", { name: "Register farm" })
    );
    expect(onSuccess).not.toHaveBeenCalled();
    expect(screen.getByText(/rainfall is required/i)).toBeInTheDocument();
    expect(screen.getByText(/temperature is required/i)).toBeInTheDocument();
  });

  it("displays submit error when onSuccess throws", async () => {
    onSuccess.mockRejectedValueOnce(new Error("Error"));
    render(<RegisterFarmForm onCancel={onCancel} onSuccess={onSuccess} />);
    await userEvent.type(screen.getByLabelText(/rainfall/i), "800");
    await userEvent.type(screen.getByLabelText(/temperature/i), "22");
    await userEvent.type(screen.getByLabelText(/elevation/i), "150");
    await userEvent.type(screen.getByLabelText(/soil ph/i), "6.5");
    await userEvent.selectOptions(screen.getByLabelText(/soil texture/i), "1");
    await userEvent.type(screen.getByLabelText(/area/i), "5");
    await userEvent.type(screen.getByLabelText(/latitude/i), "-37.8");
    await userEvent.type(screen.getByLabelText(/longitude/i), "144.9");
    await userEvent.type(screen.getByLabelText(/slope/i), "3.2");
    await userEvent.click(screen.getByRole("button", { name: /Block/i }));

    await userEvent.click(
      screen.getByRole("button", { name: "Register farm" })
    );
    await waitFor(() =>
      expect(screen.getByText(/failed to register farm/i)).toBeInTheDocument()
    );
    expect(onCancel).not.toHaveBeenCalled();
  });

  it("clears validation errors on field change", async () => {
    const user = userEvent.setup();
    render(<RegisterFarmForm onCancel={onCancel} onSuccess={onSuccess} />);
    const registerBtn = screen.getByRole("button", { name: "Register farm" });
    await user.click(registerBtn);
    expect(screen.getByText(/rainfall is required/i)).toBeInTheDocument();

    const rainfallInput = screen.getByLabelText(/rainfall/i);
    await user.clear(rainfallInput);
    await user.type(rainfallInput, "800");
    expect(screen.queryByText(/rainfall is required/i)).not.toBeInTheDocument();
  });

  it("submits successfully after filling all required fields", async () => {
    const user = userEvent.setup();
    render(<RegisterFarmForm onCancel={onCancel} onSuccess={onSuccess} />);

    await user.type(screen.getByLabelText(/rainfall/i), "800");
    await user.type(screen.getByLabelText(/temperature/i), "22");
    await user.type(screen.getByLabelText(/elevation/i), "150");
    await user.type(screen.getByLabelText(/soil ph/i), "6.5");
    await user.selectOptions(screen.getByLabelText(/soil texture/i), "1");
    await user.type(screen.getByLabelText(/area/i), "5");
    await user.type(screen.getByLabelText(/latitude/i), "-37.8");
    await user.type(screen.getByLabelText(/longitude/i), "144.9");
    await user.type(screen.getByLabelText(/slope/i), "3.2");
    await user.click(screen.getByRole("button", { name: /Block/i }));

    await user.click(screen.getByRole("button", { name: "Register farm" }));
    await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1));
  });
});

// EditFarmModal interactions Tests
describe("EditFarmModal ", () => {
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

describe("FarmEditForm ", () => {
  const farm = mockFarm(5);
  const onCancel = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: { name: "Admin", role: "admin" },
      getAccessToken: () => "mock-token",
    });
    mockSoilTextures.mockReturnValue({
      soilTextures: [{ id: 1, name: "Loam" }],
      isLoading: false,
    });
  });

  it("clears a validation error after correcting a field", async () => {
    const user = userEvent.setup();
    render(
      <FarmEditForm farm={farm} onCancel={onCancel} onSuccess={onSuccess} />
    );
    await waitFor(() =>
      expect(screen.queryByText(/Saving…/i)).not.toBeInTheDocument()
    );
    const rainfall = screen.getByDisplayValue("1200");
    await user.clear(rainfall);
    await user.click(screen.getByText("Save changes"));
    expect(screen.getByText(/rainfall is required/i)).toBeInTheDocument();

    await user.type(rainfall, "900");
    expect(screen.queryByText(/rainfall is required/i)).not.toBeInTheDocument();
  });

  it("submits updated data correctly", async () => {
    const user = userEvent.setup();
    render(
      <FarmEditForm farm={farm} onCancel={onCancel} onSuccess={onSuccess} />
    );
    await waitFor(() =>
      expect(screen.queryByText(/Saving…/i)).not.toBeInTheDocument()
    );
    const rainfall = screen.getByDisplayValue("1200");
    await user.clear(rainfall);
    await user.type(rainfall, "900");
    await user.click(screen.getByRole("button", { name: /Coastal/i }));
    await user.click(screen.getByText("Save changes"));

    await waitFor(() =>
      expect(onSuccess).toHaveBeenCalledWith(
        5,
        expect.objectContaining({
          rainfall_mm: 900,
          coastal: true,
        })
      )
    );
  });

  it("renders with pre-filled farm values", () => {
    render(
      <FarmEditForm farm={farm} onCancel={onCancel} onSuccess={onSuccess} />
    );
    expect(screen.getByDisplayValue("1200")).toBeInTheDocument();
    expect(screen.getByDisplayValue("22")).toBeInTheDocument();
    expect(screen.getByDisplayValue("6.5")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Coastal/i })).not.toBeChecked();
  });

  it("updates a field and clears its error", async () => {
    render(
      <FarmEditForm farm={farm} onCancel={onCancel} onSuccess={onSuccess} />
    );
    await waitFor(() =>
      expect(screen.queryByText(/Saving…/i)).not.toBeInTheDocument()
    );
    const rainfall = screen.getByDisplayValue("1200");
    await userEvent.clear(rainfall);
    await userEvent.click(screen.getByText("Save changes"));
    expect(screen.getByText(/rainfall is required/i)).toBeInTheDocument();

    await userEvent.type(rainfall, "900");
    expect(screen.queryByText(/rainfall is required/i)).not.toBeInTheDocument();
  });

  it("toggles boolean fields", async () => {
    render(
      <FarmEditForm farm={farm} onCancel={onCancel} onSuccess={onSuccess} />
    );
    const coastal = screen.getByRole("button", { name: /Coastal/i });
    expect(coastal).not.toHaveClass("register-farm-toggle-active");
    await userEvent.click(coastal);
    expect(coastal).toHaveClass("register-farm-toggle-active");
  });

  it("submits changes and calls onSuccess with farm id and updated payload", async () => {
    render(
      <FarmEditForm farm={farm} onCancel={onCancel} onSuccess={onSuccess} />
    );
    await waitFor(() =>
      expect(screen.queryByText(/Saving…/i)).not.toBeInTheDocument()
    );
    const rainfall = screen.getByDisplayValue("1200");
    await userEvent.clear(rainfall);
    await userEvent.type(rainfall, "900");
    await userEvent.click(screen.getByRole("button", { name: /Coastal/i }));
    await userEvent.click(screen.getByText("Save changes"));

    await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1));
    expect(onSuccess).toHaveBeenCalledWith(
      5,
      expect.objectContaining({
        rainfall_mm: 900,
        coastal: true,
      })
    );
  });

  it("shows validation errors when required field is missing", async () => {
    render(
      <FarmEditForm farm={farm} onCancel={onCancel} onSuccess={onSuccess} />
    );
    await waitFor(() =>
      expect(screen.queryByText(/Saving…/i)).not.toBeInTheDocument()
    );
    const rainfall = screen.getByDisplayValue("1200");
    await userEvent.clear(rainfall);
    await userEvent.click(screen.getByText("Save changes"));
    expect(onSuccess).not.toHaveBeenCalled();
    expect(screen.getByText(/rainfall is required/i)).toBeInTheDocument();
  });

  it("shows error when onSuccess throws", async () => {
    onSuccess.mockRejectedValueOnce(new Error("Server error"));
    render(
      <FarmEditForm farm={farm} onCancel={onCancel} onSuccess={onSuccess} />
    );
    await waitFor(() =>
      expect(screen.queryByText(/Saving…/i)).not.toBeInTheDocument()
    );
    await userEvent.click(screen.getByText("Save changes"));
    await waitFor(() =>
      expect(screen.getByText(/failed to update farm/i)).toBeInTheDocument()
    );
  });
});
