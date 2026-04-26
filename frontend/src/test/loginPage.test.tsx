import "@testing-library/jest-dom/vitest";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";

import LoginPage from "../pages/auth/LoginPage";

const mockLogin = vi.fn();
const mockNavigate = vi.fn();

// Hoist the auth mock so we can dynamically change the user state per test
const mockAuthContext = vi.hoisted(() => ({
  useAuth: vi.fn(),
}));

vi.mock("../contexts/AuthContext", () => ({
  useAuth: mockAuthContext.useAuth,
}));

vi.mock("react-router-dom", async () => {
  const actual =
    await vi.importActual<typeof import("react-router-dom")>(
      "react-router-dom"
    );
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

function renderLoginPage() {
  return render(
    <HelmetProvider>
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    </HelmetProvider>
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default state: not logged in
    mockAuthContext.useAuth.mockReturnValue({
      login: mockLogin,
      isLoading: false,
      user: null,
    });
  });

  it("renders the login page content", () => {
    renderLoginPage();

    // Matches the new h1 text
    expect(
      screen.getByRole("heading", { name: /sign in to your account/i })
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/enter your email/i)
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/enter your password/i)
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /sign in/i })
    ).toBeInTheDocument();
  });

  it("submits credentials correctly when sign in is clicked", async () => {
    mockLogin.mockResolvedValueOnce(undefined);

    renderLoginPage();

    await userEvent.type(
      screen.getByPlaceholderText(/enter your email/i),
      "admin@test.com"
    );
    await userEvent.type(
      screen.getByPlaceholderText(/enter your password/i),
      "Password123!"
    );
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: "admin@test.com",
        password: "Password123!",
      });
    });
  });

  // Tests the useEffect admin redirect
  it("redirects to /admin automatically if user has admin role", () => {
    mockAuthContext.useAuth.mockReturnValue({
      login: mockLogin,
      isLoading: false,
      user: { role: "admin" },
    });

    renderLoginPage();

    expect(mockNavigate).toHaveBeenCalledWith("/admin");
  });

  // Tests the useEffect supervisor redirect
  it("redirects to / automatically if user has supervisor role", () => {
    mockAuthContext.useAuth.mockReturnValue({
      login: mockLogin,
      isLoading: false,
      user: { role: "supervisor" },
    });

    renderLoginPage();

    expect(mockNavigate).toHaveBeenCalledWith("/");
  });

  it("shows validation messages for empty fields", async () => {
    renderLoginPage();

    // Because the submit button is disabled when fields are empty,
    // we trigger the validation by clicking and tabbing away (onBlur)
    await userEvent.click(screen.getByPlaceholderText(/enter your email/i));
    await userEvent.tab();
    await userEvent.tab();

    expect(await screen.findByText("Email is required.")).toBeInTheDocument();
    expect(
      await screen.findByText("Password is required.")
    ).toBeInTheDocument();

    expect(mockLogin).not.toHaveBeenCalled();
  });

  it("shows backend error message when login fails", async () => {
    mockLogin.mockRejectedValueOnce(new Error("Invalid credentials"));

    renderLoginPage();

    await userEvent.type(
      screen.getByPlaceholderText(/enter your email/i),
      "admin@test.com"
    );
    await userEvent.type(
      screen.getByPlaceholderText(/enter your password/i),
      "wrong-password"
    );
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText("Invalid credentials")).toBeInTheDocument();
    });

    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
