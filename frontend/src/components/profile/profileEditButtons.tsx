import { useAuth } from "@/contexts/AuthContext";

interface ProfileEditProps {
  onAdd?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

export default function ProfileEditActions({
  onAdd,
  onEdit,
  onDelete,
}: ProfileEditProps) {
  // Call user details from context
  const { user } = useAuth();

  // Officer role cannot add, edit or delete, supervisor can read and edit
  // If user is admin show all post buttons, component is non-functional and currently cosmetic
  const canEdit = user?.role === "supervisor" || user?.role === "admin";
  const canAdd = user?.role === "admin";
  const canDelete = user?.role === "admin";

  if (!canAdd && !canEdit && !canDelete) return null;

  return (
    <div className="farmActions">
      {canDelete && (
        <button
          className="farmActionBtn farmActionBtnDanger"
          onClick={onDelete}
        >
          🗑️ Delete
        </button>
      )}
      {canEdit && (
        <button className="farmActionBtn" onClick={onEdit}>
          ✏️ Edit
        </button>
      )}
      {canAdd && (
        <button className="farmActionBtn" onClick={onAdd}>
          ➕ Add
        </button>
      )}
    </div>
  );
}
