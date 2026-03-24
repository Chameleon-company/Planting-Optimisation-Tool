import React, { ErrorInfo } from "react";
import { ErrorBoundary, FallbackProps } from "react-error-boundary";

interface BackendError {
  detail: string;
  errors?: { field: string; message: string }[];
}

const logError = (error: unknown, info: ErrorInfo) => {
  console.error("[ErrorBoundary]", error, info);
};

const ErrorFallback = ({ error, resetErrorBoundary }: FallbackProps) => {
  const backendError =
    typeof error === "object" && error !== null && "detail" in error
      ? (error as BackendError)
      : null;

  const detail =
    backendError?.detail ??
    (error instanceof Error
      ? error.message
      : "An unexpected error occurred. Please try again.");

  const fieldErrors = backendError?.errors ?? [];

  return (
    <div className="global-error-boundary-text" role="alert">
      <h2>Something went wrong</h2>
      <p>{detail}</p>
      {fieldErrors.length > 0 && (
        <ul>
          {fieldErrors.map((e, i) => (
            <li key={i}>
              {" "}
              {e.field}: {e.message}
            </li>
          ))}
        </ul>
      )}
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
};

export default function GlobalErrorBoundary({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={logError}
      onReset={() => {}}
    >
      {children}
    </ErrorBoundary>
  );
}
