import "@testing-library/jest-dom/vitest";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import ResetPasswordPage from "../pages/auth/ResetPasswordPage";
import { useValidateResetToken } from "../hooks/useValidateResetToken";

const mockResetPassword = vi.fn();

const mockResetPasswordHook = vi.hoisted(() => ({
  useResetPassword: vi.fn(),
}));

vi.mock("../hooks/useResetPassword", () => ({
  useResetPassword: mockResetPasswordHook.useResetPassword,
}));
vi.mock("../hooks/useValidateResetToken", () => ({
  useValidateResetToken: vi.fn(),
}));

function renderResetPasswordPage(route = "/reset-password?token=reset-token") {
  return render(
    <HelmetProvider>
      <MemoryRouter initialEntries={[route]}>
        <ResetPasswordPage />
      </MemoryRouter>
    </HelmetProvider>
  );
}

describe("ResetPasswordPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockResetPasswordHook.useResetPassword.mockReturnValue({
      resetPassword: mockResetPassword,
      isLoading: false,
      errorMessage: "",
      successMessage: "",
    });

    vi.mocked(useValidateResetToken).mockReturnValue({
      isCheckingToken: false,
      tokenErrorMessage: "",
    });
  });

  it("renders the reset password form when token exists", () => {
    renderResetPasswordPage();

    expect(
      screen.getByRole("heading", { name: /reset your password/i })
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/^new password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^confirm password$/i)).toBeInTheDocument();
    expect(
      screen.getByText(
        /password must be at least 8 characters and include uppercase, lowercase, number, and special character/i
      )
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /your reset link can only be used once and expires after 10 minutes/i
      )
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /request a new reset link/i })
    ).toHaveAttribute("href", "/forgot-password");
  });

  it("shows checking message while reset token is being validated", () => {
    vi.mocked(useValidateResetToken).mockReturnValue({
      isCheckingToken: true,
      tokenErrorMessage: "",
    });

    renderResetPasswordPage();

    expect(
      screen.getByRole("heading", { name: /checking reset link/i })
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /please wait while we validate your password reset link/i
      )
    ).toBeInTheDocument();

    expect(
      screen.queryByRole("button", { name: /reset password/i })
    ).not.toBeInTheDocument();
  });

  it("shows invalid reset link message when token validation fails", () => {
    vi.mocked(useValidateResetToken).mockReturnValue({
      isCheckingToken: false,
      tokenErrorMessage: "Invalid or expired token",
    });

    renderResetPasswordPage();

    expect(
      screen.getByRole("heading", { name: /invalid reset link/i })
    ).toBeInTheDocument();

    expect(screen.getByText("Invalid or expired token")).toBeInTheDocument();

    expect(
      screen.getByRole("link", { name: /request new reset link/i })
    ).toHaveAttribute("href", "/forgot-password");

    expect(
      screen.queryByRole("button", { name: /reset password/i })
    ).not.toBeInTheDocument();
  });

  it("shows invalid reset link state when token is missing", () => {
    renderResetPasswordPage("/reset-password");

    expect(
      screen.getByRole("heading", { name: /invalid reset link/i })
    ).toBeInTheDocument();
    expect(
      screen.getByText(/this reset link is missing a token/i)
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /request new reset link/i })
    ).toHaveAttribute("href", "/forgot-password");
    expect(screen.queryByLabelText(/^new password$/i)).not.toBeInTheDocument();
  });

  it("shows required validation when password fields are empty", async () => {
    renderResetPasswordPage();

    await userEvent.click(
      screen.getByRole("button", { name: /reset password/i })
    );

    expect(
      await screen.findByText("New password is required.")
    ).toBeInTheDocument();
    expect(
      await screen.findByText("Confirm password is required.")
    ).toBeInTheDocument();
    expect(mockResetPassword).not.toHaveBeenCalled();
  });

  it("shows password complexity validation errors", async () => {
    renderResetPasswordPage();

    await userEvent.type(screen.getByLabelText(/^new password$/i), "password");
    await userEvent.type(
      screen.getByLabelText(/^confirm password$/i),
      "password"
    );
    await userEvent.click(
      screen.getByRole("button", { name: /reset password/i })
    );

    expect(
      screen.getByText("Must contain at least one uppercase letter.")
    ).toBeInTheDocument();
    expect(
      screen.getByText("Must contain at least one number.")
    ).toBeInTheDocument();
    expect(
      screen.getByText("Must contain at least one special character.")
    ).toBeInTheDocument();
    expect(mockResetPassword).not.toHaveBeenCalled();
  });

  it("shows password mismatch validation", async () => {
    renderResetPasswordPage();

    await userEvent.type(
      screen.getByLabelText(/^new password$/i),
      "Password1234@"
    );
    await userEvent.type(
      screen.getByLabelText(/^confirm password$/i),
      "Password12345@"
    );
    await userEvent.click(
      screen.getByRole("button", { name: /reset password/i })
    );

    expect(screen.getByText("Passwords do not match.")).toBeInTheDocument();
    expect(mockResetPassword).not.toHaveBeenCalled();
  });

  it("toggles both password fields between hidden and visible", async () => {
    renderResetPasswordPage();

    const newPasswordInput = screen.getByLabelText(/^new password$/i);
    const confirmPasswordInput = screen.getByLabelText(/^confirm password$/i);

    expect(newPasswordInput).toHaveAttribute("type", "password");
    expect(confirmPasswordInput).toHaveAttribute("type", "password");

    const toggleButtons = screen.getAllByRole("button", { name: /show/i });

    await userEvent.click(toggleButtons[0]);
    await userEvent.click(toggleButtons[1]);

    expect(newPasswordInput).toHaveAttribute("type", "text");
    expect(confirmPasswordInput).toHaveAttribute("type", "text");

    const hideButtons = screen.getAllByRole("button", { name: /hide/i });

    await userEvent.click(hideButtons[0]);
    await userEvent.click(hideButtons[1]);

    expect(newPasswordInput).toHaveAttribute("type", "password");
    expect(confirmPasswordInput).toHaveAttribute("type", "password");
  });

  it("submits token and valid new password", async () => {
    mockResetPassword.mockResolvedValueOnce(undefined);

    renderResetPasswordPage("/reset-password?token=abc123");

    await userEvent.type(
      screen.getByLabelText(/^new password$/i),
      "Password1234@"
    );
    await userEvent.type(
      screen.getByLabelText(/^confirm password$/i),
      "Password1234@"
    );
    await userEvent.click(
      screen.getByRole("button", { name: /reset password/i })
    );

    expect(mockResetPassword).toHaveBeenCalledWith("abc123", "Password1234@");
  });

  it("redirects to login after a successful password reset", async () => {
    mockResetPassword.mockResolvedValueOnce(true);

    render(
      <HelmetProvider>
        <MemoryRouter initialEntries={["/reset-password?token=abc123"]}>
          <Routes>
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/login" element={<h1>Login route reached</h1>} />
          </Routes>
        </MemoryRouter>
      </HelmetProvider>
    );

    await userEvent.type(
      screen.getByLabelText(/^new password$/i),
      "Password1234@"
    );
    await userEvent.type(
      screen.getByLabelText(/^confirm password$/i),
      "Password1234@"
    );
    await userEvent.click(
      screen.getByRole("button", { name: /reset password/i })
    );

    expect(mockResetPassword).toHaveBeenCalledWith("abc123", "Password1234@");
    expect(
      await screen.findByRole("heading", { name: /login route reached/i })
    ).toBeInTheDocument();
  });

  it("shows loading state while reset is in progress", () => {
    mockResetPasswordHook.useResetPassword.mockReturnValue({
      resetPassword: mockResetPassword,
      isLoading: true,
      errorMessage: "",
      successMessage: "",
    });

    renderResetPasswordPage();

    expect(
      screen.getByRole("button", { name: /resetting password/i })
    ).toBeDisabled();
  });

  it("shows success state after password reset", () => {
    mockResetPasswordHook.useResetPassword.mockReturnValue({
      resetPassword: mockResetPassword,
      isLoading: false,
      errorMessage: "",
      successMessage: "Password reset successfully. You can now sign in.",
    });

    renderResetPasswordPage();

    expect(
      screen.getByRole("heading", { name: /password reset successful/i })
    ).toBeInTheDocument();
    expect(
      screen.getByText("Password reset successfully. You can now sign in.")
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /back to sign in/i })
    ).toHaveAttribute("href", "/login");
  });

  it("shows error state from the hook", () => {
    mockResetPasswordHook.useResetPassword.mockReturnValue({
      resetPassword: mockResetPassword,
      isLoading: false,
      errorMessage: "Invalid or expired token",
      successMessage: "",
    });

    renderResetPasswordPage();

    expect(screen.getByText("Invalid or expired token")).toBeInTheDocument();
    expect(
      screen.queryByText(
        /your reset link can only be used once and may expire/i
      )
    ).not.toBeInTheDocument();
  });
});
