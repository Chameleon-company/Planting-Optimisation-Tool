import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

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
          <button className="btn-primary" onClick={onEdit}>
            ✏️ Edit
          </button>
        )}
        {canAdd && (
          <button className="btn-primary" onClick={onAdd}>
            ➕ Register
          </button>
        )}
      </div>

      {showDeleteConfirm && (
        <div className="delete-modal-overlay" onClick={handleCancelDelete}>
          <div className="delete-modal" onClick={e => e.stopPropagation()}>
            <h3 className="delete-modal-title">Delete Farm</h3>
            <p className="delete-modal-message">
              Are you sure you want to delete this farm? This action cannot be
              undone.
            </p>
            <div className="delete-modal-actions">
              <button className="btn-primary" onClick={handleCancelDelete}>
                Cancel
              </button>
              <button className="btn-danger" onClick={handleConfirmDelete}>
                🗑️ Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
