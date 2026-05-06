import { it, expect, describe, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import GlobalWeightsPage from "@/pages/admin/settings/GlobalWeightsPage";
import { useGlobalWeightRuns } from "@/hooks/useGlobalWeightRuns";
import { useEpiScoring } from "@/hooks/useEpiScoring";

// Mock the custom hooks
vi.mock("@/hooks/useGlobalWeightRuns");
vi.mock("@/hooks/useEpiScoring");

describe("GlobalWeightsPage", () => {
  const mockUploadCsv = vi.fn();
  const mockProcessEpiCsv = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    // Default mock implementation for useGlobalWeightRuns
    vi.mocked(useGlobalWeightRuns).mockReturnValue({
      runs: [],
      isLoading: false,
      error: null,
      uploadCsv: mockUploadCsv,
      fetchRunDetails: vi.fn(),
      deleteRun: vi.fn(),
    });

    // Default mock implementation for useEpiScoring
    vi.mocked(useEpiScoring).mockReturnValue({
      processEpiCsv: mockProcessEpiCsv,
      isEpiLoading: false,
      epiError: null,
    });
  });

  const renderPage = () => {
    return render(
      <HelmetProvider>
        <MemoryRouter>
          <GlobalWeightsPage />
        </MemoryRouter>
      </HelmetProvider>
    );
  };

  it("renders the header and navigation link", () => {
    renderPage();
    expect(screen.getByText(/Back to Weighting Methods/i)).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 2, name: /^Global Weights$/i })
    ).toBeInTheDocument();
  });

  it("triggers uploadCsv when a file is selected for Global Weights", () => {
    renderPage();
    const file = new File(["test data"], "weights.csv", { type: "text/csv" });
    const input = screen.getByLabelText(
      /Select & Upload CSV/i
    ) as HTMLInputElement;

    // Simulate file selection
    fireEvent.change(input, { target: { files: [file] } });

    expect(mockUploadCsv).toHaveBeenCalledWith(file);
  });

  it("triggers processEpiCsv when a file is selected for EPI processing", () => {
    renderPage();
    const file = new File(["epi data"], "epi.csv", { type: "text/csv" });
    const input = screen.getByLabelText(/Process EPI CSV/i) as HTMLInputElement;

    fireEvent.change(input, { target: { files: [file] } });

    expect(mockProcessEpiCsv).toHaveBeenCalledWith(file);
  });

  it("displays error messages formatted as a list when they occur", () => {
    const multiError = "Row 1: Missing ID | Row 2: Invalid Score";
    vi.mocked(useGlobalWeightRuns).mockReturnValue({
      runs: [],
      isLoading: false,
      error: multiError,
      uploadCsv: vi.fn(),
      fetchRunDetails: vi.fn(),
      deleteRun: vi.fn(),
    });

    renderPage();

    // Verify error parsing logic (split by " | ")
    expect(screen.getByText(/Row 1: Missing ID/i)).toBeInTheDocument();
    expect(screen.getByText(/Row 2: Invalid Score/i)).toBeInTheDocument();
  });

  it("shows loading state on buttons during processing", () => {
    vi.mocked(useEpiScoring).mockReturnValue({
      processEpiCsv: vi.fn(),
      isEpiLoading: true,
      epiError: null,
    });

    renderPage();

    expect(
      screen.getByText(/Processing & Downloading.../i)
    ).toBeInTheDocument();
  });
});
