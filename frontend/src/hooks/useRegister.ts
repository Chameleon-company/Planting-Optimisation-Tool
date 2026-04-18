import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL;

interface RegisterData {
  name: string;
  email: string;
  password: string;
  role: string;
}

export function useRegister() {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const register = async (data: RegisterData) => {
    setIsLoading(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        let errorText = "Registration failed. Please try again.";
        try {
          const errorData = await response.json();
          errorText = errorData.detail || errorText;
        } catch {
          // Keep default message
        }
        throw new Error(errorText);
      }

      setSuccessMessage(
        "Registration successful. Check your email to verify your account."
      );
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Registration failed. Please try again.";
      setErrorMessage(message);
    } finally {
      setIsLoading(false);
    }
  };

  return { register, isLoading, errorMessage, successMessage };
}
