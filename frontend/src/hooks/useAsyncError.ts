import { useState, useCallback } from "react";

export const useAsyncError = () => {
  const [, setError] = useState();

  return useCallback(
    // Change 'any' to 'unknown'
    (e: unknown) => {
      setError(() => {
        throw e;
      });
    },
    [setError]
  );
};
