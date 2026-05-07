import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL;

export function useForgotPassword() {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const forgotPassword = async (email: string) => {
    setIsLoading(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const response = await fetch(`${API_BASE}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        let errorText = "Unable to send reset link. Please try again.";
        try {
          const errorData = await response.json();
          errorText = errorData.detail || errorText;
        } catch {
          // Keep default message
        }
        throw new Error(errorText);
      }

      setSuccessMessage(
        "Please check your inbox for a password reset link. If this email is registered, the link will arrive shortly."
      );
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Unable to send reset link. Please try again.";
      setErrorMessage(message);
    } finally {
      setIsLoading(false);
    }
  };

  return { forgotPassword, isLoading, errorMessage, successMessage };
}
