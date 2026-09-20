import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../contexts/AuthContext";
import {
  GlobalWeightsRunSummary,
  GlobalWeightItem,
} from "@/utils/globalWeightHelpers";
import { apiFetch } from "@/utils/apifetch";

// Helper to reliably extract the error message from FastAPI responses.
async function extractErrorMessage(
  response: Response,
  defaultMessage: string
): Promise<string> {
  try {
    const data = await response.json();

    if (data && data.detail) {
      // Handle Pydantic 422 validation arrays.
      if (Array.isArray(data.detail)) {
        return data.detail.map((err: { msg: string }) => err.msg).join(" | ");
      }

      // Handle standard HTTPException strings.
      if (typeof data.detail === "string") {
        return data.detail;
      }
    }
  } catch {
    return `Server Error (${response.status}): ${defaultMessage}`;
  }

  return defaultMessage;
}

export function useGlobalWeightRuns() {
  const { user } = useAuth();

  const [runs, setRuns] = useState<GlobalWeightsRunSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRuns = useCallback(async () => {
    if (!user) {
      setRuns([]);
      setError("You must be logged in to view global weight runs.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiFetch("/global-weights/runs");

      if (!response.ok) {
        throw new Error(
          await extractErrorMessage(
            response,
            "Failed to fetch global weight runs"
          )
        );
      }

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
  }, [user]);

  useEffect(() => {
    void fetchRuns();
  }, [fetchRuns]);

  const uploadCsv = async (file: File) => {
    if (!user) {
      setError("You must be logged in to import global weights.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await apiFetch("/global-weights/import", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(
          await extractErrorMessage(response, "Failed to import CSV")
        );
      }

      // Refresh the list after successful import.
      await fetchRuns();
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

  const fetchRunDetails = useCallback(
    async (runId: string): Promise<GlobalWeightItem[]> => {
      if (!user) {
        throw new Error(
          "You must be logged in to view global weight run details."
        );
      }

      const response = await apiFetch(`/global-weights/runs/${runId}`);

      if (!response.ok) {
        throw new Error(
          await extractErrorMessage(response, "Failed to fetch run details")
        );
      }

      const data = await response.json();

      return data.weights || [];
    },
    [user]
  );

  const deleteRun = async (runId: string) => {
    if (!user) {
      setError("You must be logged in to delete global weight runs.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiFetch(`/global-weights/runs/${runId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(
          await extractErrorMessage(response, "Failed to delete the run")
        );
      }

      // Refresh the table after successful deletion.
      await fetchRuns();
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

  return {
    runs,
    isLoading,
    error,
    uploadCsv,
    fetchRunDetails,
    deleteRun,
  };
}
