import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8080";

export function useValidateResetToken(token: string) {
  const [isCheckingToken, setIsCheckingToken] = useState(false);
  const [tokenErrorMessage, setTokenErrorMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setTokenErrorMessage(
        "This reset link is missing a token. Please request a new password reset email."
      );
      return;
    }

    const controller = new AbortController();

    async function validateToken() {
      setIsCheckingToken(true);
      setTokenErrorMessage("");

      try {
        const response = await fetch(
          `${API_BASE}/auth/reset-password/validate?token=${encodeURIComponent(token)}`,
          {
            method: "GET",
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          let errorText = "Invalid or expired reset link.";

          try {
            const errorData = await response.json();
            errorText = errorData.detail || errorText;
          } catch {
            // Keep default error message.
          }

          setTokenErrorMessage(errorText);
        }
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setTokenErrorMessage(
          "Unable to validate reset link. Please request a new password reset email."
        );
      } finally {
        setIsCheckingToken(false);
      }
    }

    validateToken();

    return () => {
      controller.abort();
    };
  }, [token]);

  return {
    isCheckingToken,
    tokenErrorMessage,
  };
}
