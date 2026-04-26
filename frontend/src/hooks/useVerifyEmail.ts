import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL;

type VerifyStatus = "loading" | "success" | "error";

export function useVerifyEmail() {
  const [status, setStatus] = useState<VerifyStatus>("loading");
  const [errorMessage, setErrorMessage] = useState("");

  const verify = async (token: string) => {
    setStatus("loading");
    setErrorMessage("");

    try {
      const response = await fetch(`${API_BASE}/auth/verify-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token }),
      });

      if (!response.ok) {
        let errorText = "Invalid or expired verification link.";
        try {
          const data = await response.json();
          errorText = data.detail || errorText;
        } catch {
          // keep default
        }
        throw new Error(errorText);
      }

      setStatus("success");
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Verification failed. Please try again."
      );
      setStatus("error");
    }
  };

  return { status, errorMessage, verify };
}
