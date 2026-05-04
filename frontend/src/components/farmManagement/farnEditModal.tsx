import { useEffect } from "react";
import FarmEditForm from "./farmForms/farmEditForm";
import { Farm } from "@/hooks/useUserProfiles";
import { FarmUpdatePayload } from "@/hooks/useFarms";

interface EditFarmModalProps {
  farm: Farm;
  onClose: () => void;
  onSuccess: (farmId: number, payload: FarmUpdatePayload) => Promise<void>;
}

export default function EditFarmModal({
  farm,
  onClose,
  onSuccess,
}: EditFarmModalProps) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  return (
    <div
      className="farms-modal-overlay"
      onClick={e => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="farms-modal">
        <div className="farms-modal-header">
          <h2 className="farms-modal-title">Edit farm #{farm.id}</h2>
          <button className="farms-modal-close" onClick={onClose}>
            ✕
          </button>
        </div>
        <div className="farms-modal-body">
          <FarmEditForm farm={farm} onSuccess={onSuccess} onCancel={onClose} />
        </div>
      </div>
    </div>
  );
}
