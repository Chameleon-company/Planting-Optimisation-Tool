import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL;

export function useResetPassword() {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const resetPassword = async (token: string, newPassword: string) => {
    setIsLoading(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const response = await fetch(`${API_BASE}/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword }),
      });

      if (!response.ok) {
        let errorText = "Unable to reset password. Please try again.";
        try {
          const errorData = await response.json();
          errorText = errorData.detail || errorText;
        } catch {
          // Keep default message
        }
        throw new Error(errorText);
      }

      setSuccessMessage("Password reset successfully. You can now sign in.");
      return true;
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Unable to reset password. Please try again.";
      setErrorMessage(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  return { resetPassword, isLoading, errorMessage, successMessage };
}
