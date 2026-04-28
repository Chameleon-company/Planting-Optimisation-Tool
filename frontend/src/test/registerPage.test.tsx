// registerPage.test.tsx
//
// Tests for the RegisterPage UI component.
//
// Strategy: mock the useRegister hook so this test file only cares about
// what the component renders and whether it calls register() correctly.
// The hook's own behavior (fetch calls, API errors) is tested separately
// in useRegister.test.ts.

import "@testing-library/jest-dom/vitest";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";

import RegisterPage from "../pages/auth/RegisterPage";

// Mock the useRegister hook so tests control what it returns.
// This keeps the page test focused on UI behaviour only.
vi.mock("../hooks/useRegister", () => ({
  useRegister: vi.fn(),
}));

import { useRegister } from "../hooks/useRegister";

// Default hook return value - idle state, no messages
const defaultHookReturn = {
  register: vi.fn(),
  isLoading: false,
  errorMessage: "",
  successMessage: "",
};

function renderRegisterPage() {
  return render(
    <HelmetProvider>
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>
    </HelmetProvider>
  );
}

describe("RegisterPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset to idle state before each test
    vi.mocked(useRegister).mockReturnValue({
      ...defaultHookReturn,
      register: vi.fn(),
    });
  });

  it("renders the registration form", () => {
    renderRegisterPage();

    expect(
      screen.getByRole("heading", { name: /create your account/i })
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/enter your full name/i)
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/enter your email/i)
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/enter your password/i)
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/confirm your password/i)
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /create account/i })
    ).toBeInTheDocument();
  });

  it("calls register with the correct form data on submit", async () => {
    const mockRegister = vi.fn();
    vi.mocked(useRegister).mockReturnValue({
      ...defaultHookReturn,
      register: mockRegister,
    });

    renderRegisterPage();

    await userEvent.type(
      screen.getByPlaceholderText(/enter your full name/i),
      "Test User"
    );
    await userEvent.type(
      screen.getByPlaceholderText(/enter your email/i),
      "test@example.com"
    );
    await userEvent.type(
      screen.getByPlaceholderText(/enter your password/i),
      "Password123!"
    );
    await userEvent.type(
      screen.getByPlaceholderText(/confirm your password/i),
      "Password123!"
    );
    await userEvent.click(
      screen.getByRole("button", { name: /create account/i })
    );

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        name: "Test User",
        email: "test@example.com",
        password: "Password123!",
        role: "officer", // default role value
      });
    });
  });

  it("replaces the form with a success panel when registration succeeds", () => {
    // Simulate the hook returning a success state
    vi.mocked(useRegister).mockReturnValue({
      ...defaultHookReturn,
      successMessage:
        "Registration successful. Check your email to verify your account.",
    });

    renderRegisterPage();

    // Success panel should be visible
    expect(
      screen.getByRole("heading", { name: /account created/i })
    ).toBeInTheDocument();
    expect(screen.getByText(/check your inbox/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /sign in/i })).toBeInTheDocument();

    // Form should no longer be present
    expect(
      screen.queryByPlaceholderText(/enter your full name/i)
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /create account/i })
    ).not.toBeInTheDocument();
  });

  it("displays error message for duplicate email when hook reports it", () => {
    // Simulate the hook returning an error from the backend
    vi.mocked(useRegister).mockReturnValue({
      ...defaultHookReturn,
      errorMessage: "Email already registered.",
    });

    renderRegisterPage();

    expect(screen.getByText("Email already registered.")).toBeInTheDocument();
  });

  it("displays error message for invalid password when hook reports it", () => {
    vi.mocked(useRegister).mockReturnValue({
      ...defaultHookReturn,
      errorMessage: "Password does not meet strength requirements.",
    });

    renderRegisterPage();

    expect(
      screen.getByText("Password does not meet strength requirements.")
    ).toBeInTheDocument();
  });

  it("shows validation errors for empty required fields on blur", async () => {
    renderRegisterPage();

    // Tab through name -> email -> password to trigger their onBlur handlers.
    // Each tab blurs the current field and moves focus to the next.
    await userEvent.click(screen.getByPlaceholderText(/enter your full name/i));
    await userEvent.tab(); // blurs name
    await userEvent.tab(); // blurs email
    await userEvent.tab(); // blurs password

    expect(await screen.findByText("Name is required.")).toBeInTheDocument();
    expect(await screen.findByText("Email is required.")).toBeInTheDocument();
    expect(
      await screen.findByText("Password is required.")
    ).toBeInTheDocument();

    // register() should not be called - submit button is disabled
    expect(defaultHookReturn.register).not.toHaveBeenCalled();
  });

  it("shows error when passwords do not match", async () => {
    renderRegisterPage();

    await userEvent.type(
      screen.getByPlaceholderText(/enter your full name/i),
      "Test User"
    );
    await userEvent.type(
      screen.getByPlaceholderText(/enter your email/i),
      "test@example.com"
    );
    await userEvent.type(
      screen.getByPlaceholderText(/enter your password/i),
      "Password123!"
    );
    await userEvent.type(
      screen.getByPlaceholderText(/confirm your password/i),
      "DifferentPass123!"
    );
    // Blur the confirm password field to trigger the mismatch validation
    await userEvent.tab();

    expect(
      await screen.findByText("Passwords do not match.")
    ).toBeInTheDocument();
  });
});
