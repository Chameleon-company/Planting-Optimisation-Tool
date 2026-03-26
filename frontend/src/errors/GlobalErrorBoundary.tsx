import React, { ErrorInfo } from "react";
import { ErrorBoundary, FallbackProps } from "react-error-boundary";

// Create interface to match error type as in backend
interface BackendError {
  detail: string;
  errors?: { field: string; message: string }[];
}

// Function to log error to console with relevant information if error occurs
const logError = (error: unknown, info: ErrorInfo) => {
  console.error("[ErrorBoundary]", error, info);
};

// Fallback component for error handling
const ErrorFallback = ({ error, resetErrorBoundary }: FallbackProps) => {
  // Set backendError as const, if typeof error is object, not null, and has detail in it like with backend
  // Then set that as backendError, otherwise set it to null
  const backendError =
    typeof error === "object" && error !== null && "detail" in error
      ? (error as BackendError)
      : null;

  // Set detail as that of detail in error schema, otherwise if null, and error is an instance of the
  // Error class from TS, if so, set detail as error.message, if not, set backup string as detail
  const detail =
    backendError?.detail ??
    (error instanceof Error
      ? error.message
      : "An unexpected error occurred. Please try again.");

  // Field errors are the errors given from backend, if that is null, set fieldErrors to an empty array
  const fieldErrors = backendError?.errors ?? [];

  // Return TSX component as fallback UI
  // Map fieldEroors to grid as Detail: Message | Detail: Message, etc.
  // With button to reset the ErrorBoundary and see if it works
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

// Set GlobalErrorBoundary's children to be of ReactNode type
export default function GlobalErrorBoundary({
  children,
}: {
  children: React.ReactNode;
}) {
  // Return ErrorBoundary wrapping its children, in this case its the app
  // Which then would have ErrorBoundary take priority if an error occurs
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
