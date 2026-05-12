import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { useState } from "react";
import { useForgotPassword } from "../../hooks/useForgotPassword";

function ForgotPasswordPage() {
  const { forgotPassword, isLoading, errorMessage, successMessage } =
    useForgotPassword();
  const [email, setEmail] = useState("");
  const [touched, setTouched] = useState(false);

  const emailError = touched && !email.trim() ? "Email is required." : "";
  const isDisabled = !email.trim() || isLoading;

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setTouched(true);

    if (!email.trim()) {
      return;
    }

    await forgotPassword(email.trim());
  };

  return (
    <>
      <Helmet>
        <title>Forgot Password | Planting Optimisation Tool</title>
      </Helmet>

      <main className="login-page">
        <section className="login-card">
          <div className="login-card-header">
            <span className="login-badge">Account Recovery</span>
            <h1 className="login-title">Forgot your password?</h1>
            <p className="login-subtitle">
              Enter your registered email address and we will send you a reset
              link if the account exists.
            </p>
          </div>

          <form className="login-form" onSubmit={handleSubmit} noValidate>
            <div className="login-form-group">
              <label htmlFor="forgot-email">Email address</label>
              <input
                id="forgot-email"
                type="email"
                className={`login-input ${emailError ? "login-input-error" : ""}`}
                placeholder="Enter your email"
                value={email}
                onChange={event => setEmail(event.target.value)}
                onBlur={() => setTouched(true)}
              />
              {emailError ? (
                <p className="login-field-error">{emailError}</p>
              ) : null}
            </div>

            {errorMessage ? (
              <div className="login-message login-message-error">
                {errorMessage}
              </div>
            ) : null}

            {successMessage ? (
              <div className="login-message login-message-success">
                {successMessage}
              </div>
            ) : null}

            {!errorMessage && !successMessage ? (
              <div className="login-message login-message-info">
                Enter your email to request a password reset link.
              </div>
            ) : null}

            <button
              type="submit"
              className="btn-primary login-submit-btn"
              disabled={isDisabled}
            >
              {isLoading ? "Sending reset link..." : "Send reset link"}
            </button>

            <p className="login-footer-text">
              <Link to="/login" className="login-link">
                Back to sign in
              </Link>
            </p>
          </form>
        </section>
      </main>
    </>
  );
}

export default ForgotPasswordPage;
