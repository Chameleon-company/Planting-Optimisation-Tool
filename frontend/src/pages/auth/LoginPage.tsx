import { Helmet } from "react-helmet-async";
import { useState, useEffect } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate, Link } from "react-router-dom";

function LoginPage() {
  const { login, isLoading, user } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [touched, setTouched] = useState({
    email: false,
    password: false,
  });
  const [errorMessage, setErrorMessage] = useState("");

  const emailError = touched.email && !email.trim() ? "Email is required." : "";
  const passwordError =
    touched.password && !password.trim() ? "Password is required." : "";

  // Watch for the user to populate, then redirect
  useEffect(() => {
    if (user) {
      if (user.role === "admin") {
        navigate("/admin");
      } else if (user.role === "supervisor") {
        navigate("/");
      } else {
        navigate("/"); // Default redirect
      }
    }
  }, [user, navigate]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage("");

    setTouched({
      email: true,
      password: true,
    });

    if (!email.trim() || !password.trim()) {
      return;
    }

    try {
      await login({ email, password });
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Login failed. Please try again.";
      setErrorMessage(message);
      console.error("Login failed:", error);
    }
  };

  const isDisabled = !email.trim() || !password.trim();
  return (
    <>
      <Helmet>
        <title>Login | Planting Optimisation Tool</title>
      </Helmet>

      <main className="login-page">
        <section className="login-card">
          <div className="login-card-header">
            <span className="login-badge">User Access</span>
            <h1 className="login-title">Sign in to your account</h1>
            <p className="login-subtitle">
              Access your workspace to manage tools and resources.
            </p>
          </div>

          <form className="login-form" onSubmit={handleSubmit} noValidate>
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
                  setTouched(previous => ({
                    ...previous,
                    email: true,
                  }))
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
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>

              {passwordError ? (
                <p className="login-field-error">{passwordError}</p>
              ) : null}
            </div>

            {errorMessage ? (
              <div className="login-message login-message-error">
                {errorMessage}
              </div>
            ) : (
              <div className="login-message login-message-placeholder">
                Sign in with your verified account to access the admin
                workspace.
              </div>
            )}

            <button
              type="submit"
              className="login-submit-btn"
              disabled={isLoading || isDisabled}
            >
              {isLoading ? "Signing in..." : "Sign in"}
            </button>

            <p className="login-footer-text">
              Don't have an account?{" "}
              <Link to="/register" className="login-link">
                Register
              </Link>
            </p>
          </form>
        </section>
      </main>
    </>
  );
}

export default LoginPage;
