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

  // Depending on the user's role, show certain buttons to certain roles only
  // This works with other role checks so that supervisors can only access
  // and thus edit their own farms
  const canEdit = user?.role === "supervisor" || user?.role === "admin";
  const canAdd = user?.role === "admin";
  const canDelete = user?.role === "admin";

  if (!canAdd && !canEdit && !canDelete) return null;

  return (
    <div className="farm-actions">
      {canDelete && (
        <button className="btn-danger" onClick={onDelete}>
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
  );
}
