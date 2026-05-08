import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

const API_BASE = import.meta.env.VITE_API_URL;

export function useEpiScoring() {
  const { getAccessToken } = useAuth();
  const [isEpiLoading, setIsEpiLoading] = useState(false);
  const [epiError, setEpiError] = useState<string | null>(null);

  const processEpiCsv = async (file: File) => {
    setIsEpiLoading(true);
    setEpiError(null);
    const token = getAccessToken();

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_BASE}/global-weights/epi-add-scores`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to process EPI CSV");
      }

      // Get the response as a Blob (for file download)
      const blob = await response.blob();

      // Create a temporary URL for the Blob
      const downloadUrl = window.URL.createObjectURL(blob);

      // Create a hidden anchor tag to trigger the download
      const a = document.createElement("a");
      a.href = downloadUrl;

      // Extract filename from headers if possible, otherwise fallback to the default
      const contentDisposition = response.headers.get("Content-Disposition");
      let filename = "epi_farm_species_scores_data.csv";
      if (contentDisposition && contentDisposition.includes("filename=")) {
        filename = contentDisposition.split("filename=")[1].replace(/"/g, "");
      }

      a.download = filename;
      document.body.appendChild(a);
      a.click();

      // Cleanup the DOM and memory
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setEpiError(err.message);
      } else {
        setEpiError("An unexpected error occurred.");
      }
    } finally {
      setIsEpiLoading(false);
    }
  };

  return { processEpiCsv, isEpiLoading, epiError };
}
