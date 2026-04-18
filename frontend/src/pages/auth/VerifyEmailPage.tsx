import { Helmet } from "react-helmet-async";
import { useEffect, useRef } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useVerifyEmail } from "../../hooks/useVerifyEmail";

function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const { status, errorMessage, verify } = useVerifyEmail();
  const hasVerified = useRef(false);

  useEffect(() => {
    if (token && !hasVerified.current) {
      hasVerified.current = true;
      verify(token);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <Helmet>
        <title>Verify Email | Planting Optimisation Tool</title>
      </Helmet>

      <main className="login-page">
        <section className="login-card">
          {!token ? (
            <div className="register-success">
              <div className="register-success-icon verify-email-icon--error">
                &#10007;
              </div>
              <h1 className="login-title">Invalid link</h1>
              <p className="register-success-body">
                This verification link is missing a token. Please use the link
                from your verification email.
              </p>
              <Link
                to="/login"
                className="login-submit-btn register-success-link"
              >
                Back to sign in
              </Link>
            </div>
          ) : status === "loading" ? (
            <div className="register-success">
              <h1 className="login-title">Verifying your email...</h1>
              <p className="register-success-body">Please wait a moment.</p>
            </div>
          ) : status === "success" ? (
            <div className="register-success">
              <div className="register-success-icon">&#10003;</div>
              <h1 className="login-title">Email verified!</h1>
              <p className="register-success-body">
                Your account has been activated. You can now sign in.
              </p>
              <Link
                to="/login"
                className="login-submit-btn register-success-link"
              >
                Sign in
              </Link>
            </div>
          ) : (
            <div className="register-success">
              <div className="register-success-icon verify-email-icon--error">
                &#10007;
              </div>
              <h1 className="login-title">Verification failed</h1>
              <p className="register-success-body">{errorMessage}</p>
              <Link
                to="/login"
                className="login-submit-btn register-success-link"
              >
                Back to sign in
              </Link>
            </div>
          )}
        </section>
      </main>
    </>
  );
}

export default VerifyEmailPage;
