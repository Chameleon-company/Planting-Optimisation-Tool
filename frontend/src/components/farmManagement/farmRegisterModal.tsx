import { useEffect } from "react";
import RegisterFarmForm from "./farmForms/farmRegisterForm";
import { FarmCreatePayload } from "@/hooks/useFarms";

interface RegisterFarmModalProps {
  onClose: () => void;
  onSuccess: (payload: FarmCreatePayload) => Promise<void>;
}

export default function RegisterFarmModal({
  onClose,
  onSuccess,
}: RegisterFarmModalProps) {
  // Create useEffect that runs every mkeyboard press, and if escape is pressed, call on close
  // Rerun when onclose is pressed to prevent hanging events
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  // useEffect to lock screen when modal is open, and return to normal when closed
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  // If user clicks outside modal section, close modal
  return (
    <div
      className="farms-modal-overlay"
      onClick={e => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="farms-modal">
        <div className="farms-modal-header">
          <h2 className="farms-modal-title">Register farm</h2>
          <button className="farms-modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="farms-modal-body">
          <RegisterFarmForm onSuccess={onSuccess} onCancel={onClose} />
        </div>
      </div>
    </div>
  );
}
