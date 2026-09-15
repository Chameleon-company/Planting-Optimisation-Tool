import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import ConfirmModal from "@/components/shared/confirmModal";

interface FarmEditProps {
  onAdd?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

export default function FarmManageActions({
  onAdd,
  onEdit,
  onDelete,
}: FarmEditProps) {
  // Call user details from context
  const { user } = useAuth();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Depending on the user's role, show certain buttons to certain roles only
  // This works with other role checks so that supervisors can only access
  // and thus edit their own farms
  const canEdit = user?.role === "supervisor" || user?.role === "admin";
  const canAdd = user?.role === "admin";
  const canDelete = user?.role === "admin";

  if (!canAdd && !canEdit && !canDelete) return null;

  const handleDeleteClick = () => {
    setShowDeleteConfirm(true);
  };

  const handleConfirmDelete = () => {
    setShowDeleteConfirm(false);
    onDelete?.();
  };

  const handleCancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  return (
    <>
      <div className="farm-actions">
        {canDelete && (
          <button className="btn-danger" onClick={handleDeleteClick}>
            🗑️ Delete
          </button>
        )}
        {canEdit && (
          <button className="btn-secondary" onClick={onEdit}>
            ✏️ Edit
          </button>
        )}
        {canAdd && (
          <button className="btn-secondary" onClick={onAdd}>
            ➕ Register
          </button>
        )}
      </div>

      {showDeleteConfirm && (
        <ConfirmModal
          title="Delete Farm"
          message="Are you sure you want to delete this farm? This action cannot be undone."
          confirmLabel="Confirm Delete"
          confirmIcon="🗑️"
          isPending={false}
          onConfirm={handleConfirmDelete}
          onCancel={handleCancelDelete}
        />
      )}
    </>
  );
}
