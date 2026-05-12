import { Helmet } from "react-helmet-async";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useState } from "react";
import { useResetPassword } from "../../hooks/useResetPassword";
import { useValidateResetToken } from "../../hooks/useValidateResetToken";

const getPasswordValidationErrors = (password: string) => {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push("Password must be at least 8 characters.");
  }

  if (!/[A-Z]/.test(password)) {
    errors.push("Must contain at least one uppercase letter.");
  }

  if (!/[a-z]/.test(password)) {
    errors.push("Must contain at least one lowercase letter.");
  }

  if (!/\d/.test(password)) {
    errors.push("Must contain at least one number.");
  }

  if (!/[^A-Za-z0-9]/.test(password)) {
    errors.push("Must contain at least one special character.");
  }

  return errors;
};

function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const navigate = useNavigate();

  const { resetPassword, isLoading, errorMessage, successMessage } =
    useResetPassword();
  const { isCheckingToken, tokenErrorMessage } = useValidateResetToken(token);

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const passwordValidationErrors =
    hasSubmitted && newPassword ? getPasswordValidationErrors(newPassword) : [];

  const newPasswordError =
    hasSubmitted && !newPassword ? "New password is required." : "";

  const confirmPasswordError =
    hasSubmitted && !confirmPassword ? "Confirm password is required." : "";

  const passwordMatchError =
    hasSubmitted &&
    newPassword &&
    confirmPassword &&
    newPassword !== confirmPassword
      ? "Passwords do not match."
      : "";

  const isInvalidToken = !token || tokenErrorMessage !== "";
  const isDisabled =
    isLoading || isCheckingToken || isInvalidToken || successMessage !== "";

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setHasSubmitted(true);

    if (
      !newPassword ||
      !confirmPassword ||
      newPassword !== confirmPassword ||
      getPasswordValidationErrors(newPassword).length > 0
    ) {
      return;
    }

    const resetSucceeded = await resetPassword(token, newPassword);

    if (resetSucceeded) {
      navigate("/login", {
        state: {
          successMessage: "Password reset successfully. You can now sign in.",
        },
      });
    }
  };

  return (
    <>
      <Helmet>
        <title>Reset Password | Planting Optimisation Tool</title>
      </Helmet>

      <main className="login-page">
        <section className="login-card">
          <div className="login-card-header">
            <span className="login-badge">Account Recovery</span>
            <h1 className="login-title">Reset your password</h1>
            <p className="login-subtitle">
              Enter and confirm your new password to regain access to your
              account.
            </p>
          </div>

          {isCheckingToken ? (
            <div className="register-success">
              <h2 className="login-title">Checking reset link</h2>
              <p className="register-success-body">
                Please wait while we validate your password reset link.
              </p>
            </div>
          ) : isInvalidToken ? (
            <div className="register-success">
              <div className="register-success-icon verify-email-icon--error">
                !
              </div>
              <h2 className="login-title">Invalid reset link</h2>
              <p className="register-success-body">
                {tokenErrorMessage ||
                  "This reset link is missing a token. Please request a new password reset email."}
              </p>
              <Link
                to="/forgot-password"
                className="btn-primary login-submit-btn register-success-link"
              >
                Request new reset link
              </Link>
            </div>
          ) : successMessage ? (
            <div className="register-success">
              <div className="register-success-icon">✓</div>
              <h2 className="login-title">Password reset successful</h2>
              <p className="register-success-body">{successMessage}</p>
              <Link
                to="/login"
                className="btn-primary login-submit-btn register-success-link"
              >
                Back to sign in
              </Link>
            </div>
          ) : (
            <form className="login-form" onSubmit={handleSubmit} noValidate>
              <div className="login-form-group">
                <div className="login-message login-message-info">
                  Password must be at least 8 characters and include uppercase,
                  lowercase, number, and special character.
                  <p>
                    Your reset link can only be used once and expires after 10
                    minutes.
                  </p>
                </div>
                <label htmlFor="new-password">New password</label>
                <div className="login-password-wrapper">
                  <input
                    id="new-password"
                    type={showNewPassword ? "text" : "password"}
                    className={`login-input login-password-input ${
                      newPasswordError ||
                      passwordMatchError ||
                      passwordValidationErrors.length > 0
                        ? "login-input-error"
                        : ""
                    }`}
                    placeholder="Enter new password"
                    value={newPassword}
                    onChange={event => setNewPassword(event.target.value)}
                  />
                  <button
                    type="button"
                    className="login-password-toggle"
                    onClick={() => setShowNewPassword(current => !current)}
                  >
                    {showNewPassword ? "Hide" : "Show"}
                  </button>
                </div>
                {newPasswordError ? (
                  <p className="login-field-error">{newPasswordError}</p>
                ) : null}
                {passwordValidationErrors.map(error => (
                  <p className="login-field-error" key={error}>
                    {error}
                  </p>
                ))}
              </div>

              <div className="login-form-group">
                <label htmlFor="confirm-password">Confirm password</label>
                <div className="login-password-wrapper">
                  <input
                    id="confirm-password"
                    type={showConfirmPassword ? "text" : "password"}
                    className={`login-input login-password-input ${
                      confirmPasswordError || passwordMatchError
                        ? "login-input-error"
                        : ""
                    }`}
                    placeholder="Confirm new password"
                    value={confirmPassword}
                    onChange={event => setConfirmPassword(event.target.value)}
                  />
                  <button
                    type="button"
                    className="login-password-toggle"
                    onClick={() => setShowConfirmPassword(current => !current)}
                  >
                    {showConfirmPassword ? "Hide" : "Show"}
                  </button>
                </div>
                {confirmPasswordError ? (
                  <p className="login-field-error">{confirmPasswordError}</p>
                ) : null}
                {passwordMatchError ? (
                  <p className="login-field-error">{passwordMatchError}</p>
                ) : null}
              </div>

              {errorMessage ? (
                <div className="login-message login-message-error">
                  {errorMessage}
                </div>
              ) : null}

              <button
                type="submit"
                className="btn-primary login-submit-btn"
                disabled={isDisabled}
              >
                {isLoading ? "Resetting password..." : "Reset password"}
              </button>

              <p className="login-footer-text">
                Link expired?{" "}
                <Link to="/forgot-password" className="login-link">
                  Request a new reset link
                </Link>
              </p>
            </form>
          )}
        </section>
      </main>
    </>
  );
}

export default ResetPasswordPage;
