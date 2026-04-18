import { Helmet } from "react-helmet-async";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useRegister } from "../../hooks/useRegister";

function RegisterPage() {
  const { register, isLoading, errorMessage, successMessage } = useRegister();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("officer");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [touched, setTouched] = useState({
    name: false,
    email: false,
    password: false,
    confirmPassword: false,
  });

  const nameError = touched.name && !name.trim() ? "Name is required." : "";
  const emailError = touched.email && !email.trim() ? "Email is required." : "";
  const passwordError =
    touched.password && !password.trim() ? "Password is required." : "";
  const confirmPasswordError =
    touched.confirmPassword && password !== confirmPassword
      ? "Passwords do not match."
      : "";

  const isDisabled =
    !name.trim() ||
    !email.trim() ||
    !password.trim() ||
    !confirmPassword.trim();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setTouched({
      name: true,
      email: true,
      password: true,
      confirmPassword: true,
    });

    if (isDisabled) return;
    if (password !== confirmPassword) return;

    await register({ name, email, password, role });
  };

  return (
    <>
      <Helmet>
        <title>Register | Planting Optimisation Tool</title>
      </Helmet>

      <main className="login-page">
        <section className="login-card">
          {successMessage ? (
            // Success state - replaces the form once registration completes
            <div className="register-success">
              <div className="register-success-icon">&#10003;</div>
              <h1 className="login-title">Account created!</h1>
              <p className="register-success-body">
                We've sent a verification email to <strong>{email}</strong>.
                <br />
                Check your inbox and click the link to activate your account.
              </p>
              <Link
                to="/login"
                className="login-submit-btn register-success-link"
              >
                Sign in
              </Link>
            </div>
          ) : (
            <>
              <div className="login-card-header">
                <span className="login-badge">New Account</span>
                <h1 className="login-title">Create your account</h1>
                <p className="login-subtitle">
                  Register to access the Planting Optimisation Tool.
                </p>
              </div>

              <form className="login-form" onSubmit={handleSubmit} noValidate>
                <div className="login-form-group">
                  <label htmlFor="name">Full name</label>
                  <input
                    id="name"
                    type="text"
                    className={`login-input ${nameError ? "login-input-error" : ""}`}
                    placeholder="Enter your full name"
                    value={name}
                    onChange={event => setName(event.target.value)}
                    onBlur={() =>
                      setTouched(previous => ({ ...previous, name: true }))
                    }
                  />
                  {nameError ? (
                    <p className="login-field-error">{nameError}</p>
                  ) : null}
                </div>

                <div className="login-form-group">
                  <label htmlFor="email">Email address</label>
                  <input
                    id="email"
                    type="email"
                    className={`login-input ${emailError ? "login-input-error" : ""}`}
                    placeholder="Enter your email"
                    value={email}
                    onChange={event => setEmail(event.target.value)}
                    onBlur={() =>
                      setTouched(previous => ({ ...previous, email: true }))
                    }
                  />
                  {emailError ? (
                    <p className="login-field-error">{emailError}</p>
                  ) : null}
                </div>

                <div className="login-form-group">
                  <label htmlFor="password">Password</label>
                  <div className="login-password-wrapper">
                    <input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      className={`login-input login-password-input ${passwordError ? "login-input-error" : ""}`}
                      placeholder="Enter your password"
                      value={password}
                      onChange={event => setPassword(event.target.value)}
                      onBlur={() =>
                        setTouched(previous => ({
                          ...previous,
                          password: true,
                        }))
                      }
                    />
                    <button
                      type="button"
                      className="login-password-toggle"
                      onClick={() => setShowPassword(previous => !previous)}
                      aria-label={
                        showPassword ? "Hide password" : "Show password"
                      }
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                  {passwordError ? (
                    <p className="login-field-error">{passwordError}</p>
                  ) : null}
                  <p className="login-password-hint">
                    Must be 8+ characters with uppercase, lowercase, number, and
                    special character.
                  </p>
                </div>

                <div className="login-form-group">
                  <label htmlFor="confirmPassword">Confirm password</label>
                  <div className="login-password-wrapper">
                    <input
                      id="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      className={`login-input login-password-input ${confirmPasswordError ? "login-input-error" : ""}`}
                      placeholder="Confirm your password"
                      value={confirmPassword}
                      onChange={event => setConfirmPassword(event.target.value)}
                      onBlur={() =>
                        setTouched(previous => ({
                          ...previous,
                          confirmPassword: true,
                        }))
                      }
                    />
                    <button
                      type="button"
                      className="login-password-toggle"
                      onClick={() =>
                        setShowConfirmPassword(previous => !previous)
                      }
                      aria-label={
                        showConfirmPassword ? "Hide password" : "Show password"
                      }
                    >
                      {showConfirmPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                  {confirmPasswordError ? (
                    <p className="login-field-error">{confirmPasswordError}</p>
                  ) : null}
                </div>

                <div className="login-form-group">
                  <label htmlFor="role">Role</label>
                  <select
                    id="role"
                    className="login-input login-select"
                    value={role}
                    onChange={event => setRole(event.target.value)}
                  >
                    <option value="officer">Officer</option>
                    <option value="supervisor">Supervisor</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                {errorMessage ? (
                  <div className="login-message login-message-error">
                    {errorMessage}
                  </div>
                ) : (
                  <div className="login-message login-message-placeholder">
                    A verification email will be sent to your address after
                    registration.
                  </div>
                )}

                <button
                  type="submit"
                  className="login-submit-btn"
                  disabled={isLoading || isDisabled}
                >
                  {isLoading ? "Registering..." : "Create account"}
                </button>

                <p className="login-footer-text">
                  Already have an account?{" "}
                  <Link to="/login" className="login-link">
                    Sign in
                  </Link>
                </p>
              </form>
            </>
          )}
        </section>
      </main>
    </>
  );
}

export default RegisterPage;
