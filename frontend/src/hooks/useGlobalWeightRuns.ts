import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import {
  GlobalWeightsRunSummary,
  GlobalWeightItem,
} from "@/utils/globalWeightHelpers";

const API_BASE = import.meta.env.VITE_API_URL;

// Helper to reliably extract the error message from FastAPI responses
async function extractErrorMessage(
  response: Response,
  defaultMessage: string
): Promise<string> {
  try {
    const data = await response.json();
    if (data && data.detail) {
      // Handle Pydantic 422 Validation Arrays
      if (Array.isArray(data.detail)) {
        return data.detail.map((err: { msg: string }) => err.msg).join(" | ");
      }
      // Handle standard HTTPException strings
      if (typeof data.detail === "string") {
        return data.detail;
      }
    }
  } catch {
    // Failsafe in case the response isn't valid JSON (e.g., 500 HTML page)
    return `Server Error (${response.status}): ${defaultMessage}`;
  }
  return defaultMessage;
}

export function useGlobalWeightRuns() {
  const { getAccessToken } = useAuth();
  const [runs, setRuns] = useState<GlobalWeightsRunSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRuns = async () => {
    setIsLoading(true);
    setError(null);
    const token = getAccessToken();

    try {
      const response = await fetch(`${API_BASE}/global-weights/runs`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok)
        throw new Error(
          await extractErrorMessage(
            response,
            "Failed to fetch global weight runs"
          )
        );

      const data: GlobalWeightsRunSummary[] = await response.json();
      setRuns(data || []);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const uploadCsv = async (file: File) => {
    setIsLoading(true);
    setError(null);
    const token = getAccessToken();

    // FastAPI expects the file as form data with the key "file"
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE}/global-weights/import`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(
          await extractErrorMessage(response, "Failed to import CSV")
        );
      }

      // On success, the backend returns { status: "success", run_id: "..." }
      // Refresh the table to show the newly imported run.
      await fetchRuns();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRunDetails = async (
    runId: string
  ): Promise<GlobalWeightItem[]> => {
    const token = getAccessToken();
    const response = await fetch(`${API_BASE}/global-weights/runs/${runId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok)
      throw new Error(
        await extractErrorMessage(response, "Failed to fetch run details")
      );

    const data = await response.json();
    return data.weights || [];
  };

  const deleteRun = async (runId: string) => {
    setIsLoading(true);
    setError(null);
    const token = getAccessToken();

    try {
      const response = await fetch(`${API_BASE}/global-weights/runs/${runId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        // Handle 404 or other errors
        throw new Error(
          await extractErrorMessage(response, "Failed to delete the run")
        );
      }

      // Refresh the table data after successful deletion
      await fetchRuns();
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return { runs, isLoading, error, uploadCsv, fetchRunDetails, deleteRun };
}
