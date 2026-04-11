import "@testing-library/jest-dom/vitest";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

import LoginPage from "../pages/auth/LoginPage";

const mockLogin = vi.fn();
const mockNavigate = vi.fn();

vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => ({
    login: mockLogin,
    isLoading: false,
  }),
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
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the login page content", () => {
    renderLoginPage();

    expect(
      screen.getByRole("heading", { name: /sign in to continue/i })
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

  it("submits credentials and redirects to /admin on successful login", async () => {
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

    expect(mockNavigate).toHaveBeenCalledWith("/admin");
  });

  it("shows validation messages for empty fields", async () => {
    renderLoginPage();

    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(
      screen.getByPlaceholderText(/enter your email/i)
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/enter your password/i)
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
