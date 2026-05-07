// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { renderHook } from "@testing-library/react";
import { act } from "react";
import { Farm } from "@/hooks/useUserProfiles";
import type { FormState } from "@/components/farmManagement/farmForms/farmConstantsForm";

import FarmsTable from "@/components/farmManagement/farmsTable";
import RegisterFarmModal from "@/components/farmManagement/farmRegisterModal";
import EditFarmModal from "@/components/farmManagement/farmsEditModal";
import { validate } from "@/components/farmManagement/farmForms/validate";
import { useFarms } from "@/hooks/useFarms";
import { FarmCreatePayload } from "@/hooks/useFarms";
import FarmsManagmentPage from "@/pages/farmManagementPage";

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

// Mock functions
const mockUseAuth = vi.fn();
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

vi.mock("@/hooks/useSoilTextures", () => ({
  useSoilTextures: () => ({
    soilTextures: [
      { id: 1, name: "Sandy Loam" },
      { id: 2, name: "Clay" },
    ],
    isLoading: false,
  }),
}));

const mockNavigate = vi.fn();
const mockRefetch = vi.fn();
vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
  mockRefetch: () => mockRefetch,
}));

const defaultProfiles = {
  farms: [mockFarm(1)],
  isLoading: false,
  error: null as string | null,
  page: 1,
  setPage: vi.fn(),
  totalFarms: 1,
  totalPages: 1,
  refetch: mockRefetch,
};

let profilesOverride: Partial<typeof defaultProfiles> = {};

vi.mock("@/hooks/useUserProfiles", () => ({
  useUserProfiles: () => ({ ...defaultProfiles, ...profilesOverride }),
}));

beforeEach(() => {
  profilesOverride = {};
  // Default to an admin user so all action buttons are visible unless overridden
  mockUseAuth.mockReturnValue({
    user: { name: "Test Admin", role: "admin" },
    getAccessToken: () => "mock-token",
  });
  vi.clearAllMocks();
});

afterEach(() => {
  vi.restoreAllMocks();
});

// FarmsHeader Tests
import FarmsHeader from "@/components/farmManagement/farmHeader";

describe("FarmsHeader", () => {
  it("renders the Farm Management title", () => {
    render(<FarmsHeader isLoading={false} totalFarms={3} />);
    // The page heading should always be visible
    expect(screen.getByText("Farm Management")).toBeInTheDocument();
  });

  it("displays the correct farm count in the badge", () => {
    render(<FarmsHeader isLoading={false} totalFarms={5} />);
    // Badge should show the count with the plural label
    expect(screen.getByText("5 farms")).toBeInTheDocument();
  });

  it("uses the singular label when there is exactly one farm", () => {
    render(<FarmsHeader isLoading={false} totalFarms={1} />);
    // Singular form should be used when count is 1
    expect(screen.getByText("1 farm")).toBeInTheDocument();
  });

  it("shows a dash in the badge while loading", () => {
    render(<FarmsHeader isLoading={true} totalFarms={0} />);
    // While data is loading the badge should render a placeholder
    expect(screen.getByText("-")).toBeInTheDocument();
  });
});

// FarmManageActions Tests
import FarmManageActions from "@/components/farmManagement/farmManagementEditButtons";

describe("FarmManageActions", () => {
  it("renders Register, Edit, and Delete for admins", () => {
    mockUseAuth.mockReturnValue({ user: { name: "Admin", role: "admin" } });
    render(<FarmManageActions />);
    // Admins have full access so all three buttons must appear
    expect(screen.getByText(/register/i)).toBeInTheDocument();
    expect(screen.getByText(/edit/i)).toBeInTheDocument();
    expect(screen.getByText(/delete/i)).toBeInTheDocument();
  });

  it("renders only Edit for supervisors", () => {
    mockUseAuth.mockReturnValue({
      user: { name: "Supervisor", role: "supervisor" },
    });
    render(<FarmManageActions />);
    // Supervisors can edit but cannot add or remove farms
    expect(screen.queryByText(/register/i)).not.toBeInTheDocument();
    expect(screen.getByText(/edit/i)).toBeInTheDocument();
    expect(screen.queryByText(/delete/i)).not.toBeInTheDocument();
  });

  it("renders nothing for users with no elevated role", () => {
    mockUseAuth.mockReturnValue({ user: { name: "Officer", role: "officer" } });
    const { container } = render(<FarmManageActions />);
    // Users without a qualifying role should see no action controls at all
    expect(container.firstChild).toBeNull();
  });

  it("renders nothing when no user is logged in", () => {
    mockUseAuth.mockReturnValue({ user: null });
    const { container } = render(<FarmManageActions />);
    // Unauthenticated visitors should see no action controls
    expect(container.firstChild).toBeNull();
  });
});

// FarmsTable Tests
describe("FarmsTable", () => {
  // Base props that all tests use
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

  it("shows a login prompt when no user is provided", () => {
    render(<FarmsTable {...baseProps} user={null} />);
    // The table should not render for unauthenticated visitors
    expect(screen.getByText(/must be logged in/i)).toBeInTheDocument();
  });

  it("shows a skeleton loader while data is being fetched", () => {
    render(<FarmsTable {...baseProps} isLoading={true} />);
    // A loading placeholder should appear while the API request is loading
    // The skeleton wrapper should be in the DOM
    expect(document.querySelector(".farms-table-skeleton")).toBeInTheDocument();
  });

  it("shows an empty state when the farm array is empty", () => {
    render(<FarmsTable {...baseProps} />);
    // A message should inform the user that no farms exist yet
    expect(screen.getByText(/no farms registered yet/i)).toBeInTheDocument();
  });

  it("renders a row for each farm passed in", () => {
    render(<FarmsTable {...baseProps} farms={[mockFarm(1), mockFarm(2)]} />);
    // Each farm should produce a visible row with its ID
    expect(screen.getByText("Farm #1")).toBeInTheDocument();
    expect(screen.getByText("Farm #2")).toBeInTheDocument();
  });

  it("renders all expected column headers", () => {
    render(<FarmsTable {...baseProps} farms={[mockFarm(1)]} />);
    // Every defined column label should appear in the table header
    [
      "Farm",
      "Coordinates",
      "Area",
      "Rainfall",
      "Soil texture",
      "Temperature",
      "Coastal",
    ].forEach(col => expect(screen.getByText(col)).toBeInTheDocument());
  });

  it("hides the pagination footer when there is only one page", () => {
    render(<FarmsTable {...baseProps} farms={[mockFarm(1)]} totalPages={1} />);
    // Navigation controls should not render with a single page
    expect(
      screen.queryByRole("button", { name: /previous/i })
    ).not.toBeInTheDocument();
  });

  it("shows pagination controls when there are multiple pages", () => {
    render(<FarmsTable {...baseProps} farms={[mockFarm(1)]} totalPages={3} />);
    // Navigation should appear whenever there is more than one page of results
    expect(
      screen.getByRole("button", { name: /previous/i })
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /next/i })).toBeInTheDocument();
  });
});

// RegisterFarmModal Tests
describe("RegisterFarmModal", () => {
  it("renders the modal title", () => {
    render(<RegisterFarmModal onClose={vi.fn()} onSuccess={vi.fn()} />);
    expect(
      screen.getByRole("heading", { name: "Register farm" })
    ).toBeInTheDocument();
  });

  it("renders all required form fields", () => {
    render(<RegisterFarmModal onClose={vi.fn()} onSuccess={vi.fn()} />);
    // Every mandatory input should be present in the form
    expect(screen.getByLabelText(/rainfall/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/temperature/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/elevation/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/soil ph/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/area/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/slope/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/latitude/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/longitude/i)).toBeInTheDocument();
  });

  it("renders the Cancel and Register farm buttons", () => {
    render(<RegisterFarmModal onClose={vi.fn()} onSuccess={vi.fn()} />);
    expect(screen.getByText("Cancel")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Register farm" })
    ).toBeInTheDocument();
  });

  it("locks the page scroll while the modal is open", () => {
    render(<RegisterFarmModal onClose={vi.fn()} onSuccess={vi.fn()} />);
    // Modal should stop background scrolling
    expect(document.body.style.overflow).toBe("hidden");
  });

  it("restores page scroll when the modal unmounts", () => {
    const { unmount } = render(
      <RegisterFarmModal onClose={vi.fn()} onSuccess={vi.fn()} />
    );
    unmount();
    // Scroll lock must be released
    expect(document.body.style.overflow).toBe("");
  });
});

// EditFarmModal Tests
describe("EditFarmModal", () => {
  const farm = mockFarm(5);

  it("renders the modal title with the farm ID", () => {
    render(<EditFarmModal farm={farm} onClose={vi.fn()} onSuccess={vi.fn()} />);
    // The heading should identify which farm is being edited
    expect(screen.getByText("Edit farm #5")).toBeInTheDocument();
  });

  it("pre-populates fields with the existing farm values", () => {
    render(<EditFarmModal farm={farm} onClose={vi.fn()} onSuccess={vi.fn()} />);
    // Every numeric field should be seeded from the farm object
    expect(screen.getByDisplayValue("1200")).toBeInTheDocument(); // rainfall_mm
    expect(screen.getByDisplayValue("22")).toBeInTheDocument(); // temperature_celsius
    expect(screen.getByDisplayValue("300")).toBeInTheDocument(); // elevation_m
    expect(screen.getByDisplayValue("6.5")).toBeInTheDocument(); // ph
  });

  it("renders Save changes and Cancel buttons", () => {
    render(<EditFarmModal farm={farm} onClose={vi.fn()} onSuccess={vi.fn()} />);
    expect(screen.getByText("Save changes")).toBeInTheDocument();
    expect(screen.getByText("Cancel")).toBeInTheDocument();
  });

  it("locks the page scroll while the modal is open", () => {
    render(<EditFarmModal farm={farm} onClose={vi.fn()} onSuccess={vi.fn()} />);
    expect(document.body.style.overflow).toBe("hidden");
  });

  it("restores page scroll when the modal unmounts", () => {
    const { unmount } = render(
      <EditFarmModal farm={farm} onClose={vi.fn()} onSuccess={vi.fn()} />
    );
    unmount();
    expect(document.body.style.overflow).toBe("");
  });
});

// FarmsManagementPage render Tests
describe("FarmsManagementPage render", () => {
  it("renders the page shell with actions and table", () => {
    render(<FarmsManagmentPage />);
    expect(
      screen.getByRole("heading", { name: "Farm Management" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /register/i })
    ).toBeInTheDocument();
    expect(screen.getByRole("table")).toBeInTheDocument();
  });

  it("does not show register or edit modal on initial render", () => {
    render(<FarmsManagmentPage />);
    expect(screen.queryByTestId("register-modal")).not.toBeInTheDocument();
    expect(screen.queryByTestId("edit-modal")).not.toBeInTheDocument();
  });

  it("displays an error message when farmsError is set", () => {
    profilesOverride = { error: "Failed to load farms" };
    render(<FarmsManagmentPage />);
    expect(screen.getByText("Failed to load farms")).toBeInTheDocument();
  });

  it("does not display error paragraph when there is no error", () => {
    render(<FarmsManagmentPage />);
    expect(screen.queryByText("Failed to load farms")).not.toBeInTheDocument();
  });
});

// validate tests
const validForm: FormState = {
  rainfall_mm: "1200",
  temperature_celsius: "22",
  elevation_m: "300",
  ph: "6.5",
  soil_texture_id: "4",
  area_ha: "10.5",
  latitude: "-37.81234",
  longitude: "144.96345",
  coastal: false,
  nitrogen_fixing: false,
  shade_tolerant: false,
  bank_stabilising: false,
  slope: "5.25",
  agroforestry_type_ids: [1],
};

describe("validate", () => {
  it("returns no errors for a fully valid register form", () => {
    const errors = validate(validForm, "register");
    // A complete form should have an empty errors object
    expect(Object.keys(errors)).toHaveLength(0);
  });

  it("requires rainfall_mm", () => {
    const errors = validate({ ...validForm, rainfall_mm: "" }, "register");
    expect(errors.rainfall_mm).toBeDefined();
  });

  it("rejects rainfall below 500", () => {
    const errors = validate({ ...validForm, rainfall_mm: "499" }, "register");
    expect(errors.rainfall_mm).toMatch(/500/);
  });

  it("rejects rainfall above 3000", () => {
    const errors = validate({ ...validForm, rainfall_mm: "3001" }, "register");
    expect(errors.rainfall_mm).toMatch(/3000/);
  });

  it("rejects non-integer rainfall", () => {
    const errors = validate(
      { ...validForm, rainfall_mm: "1200.5" },
      "register"
    );
    expect(errors.rainfall_mm).toMatch(/whole number/i);
  });

  it("requires temperature_celsius", () => {
    const errors = validate(
      { ...validForm, temperature_celsius: "" },
      "register"
    );
    expect(errors.temperature_celsius).toBeDefined();
  });

  it("rejects temperature outside 15-30 range", () => {
    expect(
      validate({ ...validForm, temperature_celsius: "14" }, "register")
        .temperature_celsius
    ).toBeDefined();
    expect(
      validate({ ...validForm, temperature_celsius: "31" }, "register")
        .temperature_celsius
    ).toBeDefined();
  });

  it("requires elevation_m", () => {
    const errors = validate({ ...validForm, elevation_m: "" }, "register");
    expect(errors.elevation_m).toBeDefined();
  });

  it("rejects elevation above 2963", () => {
    const errors = validate({ ...validForm, elevation_m: "2964" }, "register");
    expect(errors.elevation_m).toBeDefined();
  });

  it("requires ph", () => {
    const errors = validate({ ...validForm, ph: "" }, "register");
    expect(errors.ph).toBeDefined();
  });

  it("rejects ph outside 4.0-8.5", () => {
    expect(validate({ ...validForm, ph: "3.9" }, "register").ph).toBeDefined();
    expect(validate({ ...validForm, ph: "8.6" }, "register").ph).toBeDefined();
  });

  it("requires soil_texture_id", () => {
    const errors = validate({ ...validForm, soil_texture_id: "" }, "register");
    expect(errors.soil_texture_id).toBeDefined();
  });

  it("requires area_ha to be greater than zero", () => {
    const errors = validate({ ...validForm, area_ha: "0" }, "register");
    expect(errors.area_ha).toBeDefined();
  });

  it("rejects area_ha above 100", () => {
    const errors = validate({ ...validForm, area_ha: "100.001" }, "register");
    expect(errors.area_ha).toBeDefined();
  });

  it("requires latitude", () => {
    const errors = validate({ ...validForm, latitude: "" }, "register");
    expect(errors.latitude).toBeDefined();
  });

  it("rejects latitude outside -90 to 90", () => {
    expect(
      validate({ ...validForm, latitude: "-91" }, "register").latitude
    ).toBeDefined();
    expect(
      validate({ ...validForm, latitude: "91" }, "register").latitude
    ).toBeDefined();
  });

  it("requires longitude", () => {
    const errors = validate({ ...validForm, longitude: "" }, "register");
    expect(errors.longitude).toBeDefined();
  });

  it("rejects longitude outside -180 to 180", () => {
    expect(
      validate({ ...validForm, longitude: "-181" }, "register").longitude
    ).toBeDefined();
    expect(
      validate({ ...validForm, longitude: "181" }, "register").longitude
    ).toBeDefined();
  });

  it("requires slope", () => {
    const errors = validate({ ...validForm, slope: "" }, "register");
    expect(errors.slope).toBeDefined();
  });

  it("rejects slope outside 0-90", () => {
    expect(
      validate({ ...validForm, slope: "-1" }, "register").slope
    ).toBeDefined();
    expect(
      validate({ ...validForm, slope: "91" }, "register").slope
    ).toBeDefined();
  });

  it("requires at least one agroforestry type in register mode", () => {
    const errors = validate(
      { ...validForm, agroforestry_type_ids: [] },
      "register"
    );
    expect(errors.agroforestry_type_ids).toBeDefined();
  });

  it("does not require agroforestry types in edit mode", () => {
    // Edit forms allow clearing agroforestry types without blocking submission
    const errors = validate(
      { ...validForm, agroforestry_type_ids: [] },
      "edit"
    );
    expect(errors.agroforestry_type_ids).toBeUndefined();
  });
});

// useFarms hook Tests

const createMockFarmPayload = (
  overrides?: Partial<FarmCreatePayload>
): FarmCreatePayload => ({
  rainfall_mm: 0,
  temperature_celsius: 0,
  elevation_m: 0,
  ph: 7,
  soil_texture_id: 1,
  area_ha: 1,
  latitude: 0,
  longitude: 0,
  coastal: false,
  riparian: false,
  nitrogen_fixing: false,
  shade_tolerant: false,
  bank_stabilising: false,
  slope: 0,
  agroforestry_type_ids: [],
  ...overrides,
});

describe("useFarms", () => {
  beforeEach(() => {
    // Ensure a valid token is returned for all hook tests
    mockUseAuth.mockReturnValue({
      user: { name: "Admin", role: "admin" },
      getAccessToken: () => "mock-token",
    });
  });

  it("createFarm sends POST with correct URL, method, headers, and body", async () => {
    const fetchSpy = vi
      .spyOn(global, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ id: 99 }), { status: 201 })
      );

    const { result } = renderHook(() => useFarms());
    const payload = {
      rainfall_mm: 1200,
      temperature_celsius: 22,
      elevation_m: 300,
      ph: 6.5,
      soil_texture_id: 4,
      area_ha: 10.5,
      latitude: -37.8,
      longitude: 144.9,
      coastal: false,
      riparian: false,
      nitrogen_fixing: true,
      shade_tolerant: false,
      bank_stabilising: false,
      slope: 5.25,
      agroforestry_type_ids: [1],
    };

    let ok: boolean;
    await act(async () => {
      ok = await result.current.createFarm(payload);
    });

    expect(ok!).toBe(true);

    const [url, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
    // Must target the /farms endpoint
    expect(url).toMatch(/\/farms$/);
    expect(init.method).toBe("POST");
    // Auth header is required for all protected endpoints
    expect((init.headers as Record<string, string>)["Authorization"]).toBe(
      "Bearer mock-token"
    );
    expect(JSON.parse(init.body as string)).toEqual(payload);
  });

  it("createFarm returns false and sets error on non-ok response", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Farm Error" }), { status: 400 })
    );

    const { result } = renderHook(() => useFarms());
    let ok: boolean;
    await act(async () => {
      ok = await result.current.createFarm(createMockFarmPayload());
    });

    // A failed request should show API error message and return false
    expect(ok!).toBe(false);
    expect(result.current.error).toBe("Farm Error");
  });

  it("updateFarm sends PUT with the farm id in the URL", async () => {
    const fetchSpy = vi
      .spyOn(global, "fetch")
      .mockResolvedValueOnce(new Response(null, { status: 200 }));

    const { result } = renderHook(() => useFarms());
    await act(async () => {
      await result.current.updateFarm(42, { rainfall_mm: 900 });
    });

    const [url, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
    // The farm id must appear in the path so the correct record is updated
    expect(url).toMatch(/\/farms\/42$/);
    expect(init.method).toBe("PUT");
    expect((init.headers as Record<string, string>)["Authorization"]).toBe(
      "Bearer mock-token"
    );
  });

  it("updateFarm returns false and sets error on failure", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Not found" }), { status: 404 })
    );

    const { result } = renderHook(() => useFarms());
    let ok: boolean;
    await act(async () => {
      ok = await result.current.updateFarm(99, {});
    });

    expect(ok!).toBe(false);
    expect(result.current.error).toBe("Not found");
  });

  it("deleteFarm sends DELETE with the farm id in the URL", async () => {
    const fetchSpy = vi
      .spyOn(global, "fetch")
      .mockResolvedValueOnce(new Response(null, { status: 204 }));

    const { result } = renderHook(() => useFarms());
    let ok: boolean;
    await act(async () => {
      ok = await result.current.deleteFarm(7);
    });

    expect(ok!).toBe(true);
    const [url, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
    expect(url).toMatch(/\/farms\/7$/);
    expect(init.method).toBe("DELETE");
    // Auth header is required for delete requests
    expect((init.headers as Record<string, string>)["Authorization"]).toBe(
      "Bearer mock-token"
    );
  });

  it("deleteFarm returns false and sets error on non-204/non-ok response", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Forbidden" }), { status: 403 })
    );

    const { result } = renderHook(() => useFarms());
    let ok: boolean;
    await act(async () => {
      ok = await result.current.deleteFarm(7);
    });

    expect(ok!).toBe(false);
    expect(result.current.error).toBe("Forbidden");
  });

  it("returns false immediately when no token is available", async () => {
    // unauthenticated state should not do anything
    mockUseAuth.mockReturnValue({ getAccessToken: () => null });
    const { result } = renderHook(() => useFarms());

    let ok: boolean;
    await act(async () => {
      ok = await result.current.createFarm(
        {} as Partial<FarmCreatePayload> as FarmCreatePayload
      );
    });
    expect(ok!).toBe(false);
  });
});
