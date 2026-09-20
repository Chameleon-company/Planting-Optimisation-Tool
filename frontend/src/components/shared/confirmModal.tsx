import { useEffect, useId, type ReactNode } from "react";
import { createPortal } from "react-dom";
import "./shared.css";

interface ConfirmModalProps {
  title: string;
  message: ReactNode;
  confirmLabel: string;
  pendingLabel?: string;
  confirmIcon?: ReactNode;
  confirmClassName?: string;
  isPending: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmModal({
  title,
  message,
  confirmLabel,
  pendingLabel,
  confirmIcon,
  confirmClassName = "confirm-modal-btn-confirm",
  isPending,
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  const titleId = useId();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  return createPortal(
    <div className="confirm-modal-backdrop" onClick={onCancel}>
      <div
        className="confirm-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={e => e.stopPropagation()}
      >
        <h3 id={titleId} className="confirm-modal-title">
          {title}
        </h3>
        <p className="confirm-modal-message">{message}</p>
        <div className="confirm-modal-actions">
          <button
            type="button"
            className="confirm-modal-btn confirm-modal-btn-cancel"
            onClick={onCancel}
          >
            Cancel
          </button>
          <button
            type="button"
            className={`confirm-modal-btn ${confirmClassName}`}
            disabled={isPending}
            onClick={onConfirm}
          >
            {confirmIcon ? <>{confirmIcon} </> : null}
            {isPending ? (pendingLabel ?? confirmLabel) : confirmLabel}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
