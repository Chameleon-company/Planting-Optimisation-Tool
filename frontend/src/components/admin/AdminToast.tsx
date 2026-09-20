import { useEffect } from "react";

export type AdminToastType = "success" | "error";

interface AdminToastProps {
  message: string;
  type: AdminToastType;
  onClose: () => void;
  durationMs?: number;
}

function AdminToast({
  message,
  type,
  onClose,
  durationMs = 4000,
}: AdminToastProps) {
  useEffect(() => {
    if (durationMs <= 0) {
      return;
    }

    const timeoutId = window.setTimeout(onClose, durationMs);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [durationMs, onClose]);

  return (
    <div
      className={`admin-toast admin-toast-${type}`}
      role={type === "error" ? "alert" : "status"}
      aria-live={type === "error" ? "assertive" : "polite"}
      aria-atomic="true"
    >
      <span>{message}</span>

      <button
        type="button"
        className="admin-toast-close"
        onClick={onClose}
        aria-label="Dismiss notification"
      >
        ×
      </button>
    </div>
  );
}

export default AdminToast;
