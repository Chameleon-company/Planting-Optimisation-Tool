import "@testing-library/jest-dom/vitest";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter } from "react-router-dom";

import ForgotPasswordPage from "../pages/auth/ForgotPasswordPage";

const mockForgotPassword = vi.fn();

const mockForgotPasswordHook = vi.hoisted(() => ({
  useForgotPassword: vi.fn(),
}));

vi.mock("../hooks/useForgotPassword", () => ({
  useForgotPassword: mockForgotPasswordHook.useForgotPassword,
}));

function renderForgotPasswordPage() {
  return render(
    <HelmetProvider>
      <MemoryRouter>
        <ForgotPasswordPage />
      </MemoryRouter>
    </HelmetProvider>
  );
}

describe("ForgotPasswordPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockForgotPasswordHook.useForgotPassword.mockReturnValue({
      forgotPassword: mockForgotPassword,
      isLoading: false,
      errorMessage: "",
      successMessage: "",
    });
  });

  it("renders the forgot password form", () => {
    renderForgotPasswordPage();

    expect(
      screen.getByRole("heading", { name: /forgot your password/i })
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /send reset link/i })
    ).toBeInTheDocument();
    expect(
      screen.getByText(/enter your email to request a password reset link/i)
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /back to sign in/i })
    ).toHaveAttribute("href", "/login");
    expect(
      screen.queryByText(/remember your password/i)
    ).not.toBeInTheDocument();
  });

  it("shows validation when email is empty", async () => {
    renderForgotPasswordPage();

    await userEvent.click(screen.getByLabelText(/email address/i));
    await userEvent.tab();

    expect(await screen.findByText("Email is required.")).toBeInTheDocument();
    expect(mockForgotPassword).not.toHaveBeenCalled();
  });

  it("submits the trimmed email address", async () => {
    mockForgotPassword.mockResolvedValueOnce(undefined);

    renderForgotPasswordPage();

    await userEvent.type(
      screen.getByLabelText(/email address/i),
      "  user@example.com  "
    );
    await userEvent.click(
      screen.getByRole("button", { name: /send reset link/i })
    );

    expect(mockForgotPassword).toHaveBeenCalledWith("user@example.com");
  });

  it("shows loading state and disables the submit button", () => {
    mockForgotPasswordHook.useForgotPassword.mockReturnValue({
      forgotPassword: mockForgotPassword,
      isLoading: true,
      errorMessage: "",
      successMessage: "",
    });

    renderForgotPasswordPage();

    expect(
      screen.getByRole("button", { name: /sending reset link/i })
    ).toBeDisabled();
  });

  it("shows success message returned by the hook", () => {
    mockForgotPasswordHook.useForgotPassword.mockReturnValue({
      forgotPassword: mockForgotPassword,
      isLoading: false,
      errorMessage: "",
      successMessage:
        "Please check your inbox for a password reset link. If this email is registered, the link will arrive shortly.",
    });

    renderForgotPasswordPage();

    expect(
      screen.getByText(/please check your inbox for a password reset link/i)
    ).toBeInTheDocument();
    expect(
      screen.queryByText(/enter your email to request a password reset link/i)
    ).not.toBeInTheDocument();
  });

  it("shows error message returned by the hook", () => {
    mockForgotPasswordHook.useForgotPassword.mockReturnValue({
      forgotPassword: mockForgotPassword,
      isLoading: false,
      errorMessage: "Unable to send reset link. Please try again.",
      successMessage: "",
    });

    renderForgotPasswordPage();

    expect(
      screen.getByText("Unable to send reset link. Please try again.")
    ).toBeInTheDocument();
    expect(
      screen.queryByText(/enter your email to request a password reset link/i)
    ).not.toBeInTheDocument();
  });
});
