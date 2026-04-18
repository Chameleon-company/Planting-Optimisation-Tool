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

  // If user exists, show add button, if user is supervisor or above, show edit button
  // If use admin is admin show delete button, component is non-functional and currently
  // Cosmetic
  const canAdd = !!user;
  const canEdit = user?.role === "supervisor" || user?.role === "admin";
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
