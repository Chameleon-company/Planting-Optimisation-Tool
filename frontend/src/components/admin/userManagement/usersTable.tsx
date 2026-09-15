import { Fragment, useState } from "react";
import { ROLES, ROLE_LABELS, type Role, type UserRead } from "@/utils/usersAPI";
import ConfirmModal from "@/components/shared/confirmModal";
import "./users.css";

interface Props {
  users: UserRead[];
  currentUserId: number | null;
  isMutating: boolean;
  onChangeRole: (userId: number, role: Role) => Promise<unknown> | void;
  onDelete: (userId: number) => Promise<unknown>;
}

// Display order for roles so that they can be sorted, highest role first
const ROLE_ORDER: Role[] = ["admin", "supervisor", "officer"];

export default function UsersTable({
  users,
  currentUserId,
  isMutating,
  onChangeRole,
  onDelete,
}: Props) {
  // Collapsed state is keyed by role so it survives re-sorts and role changes
  const [collapsed, setCollapsed] = useState<Record<Role, boolean>>({
    admin: false,
    supervisor: false,
    officer: false,
  });

  // The user awaiting delete confirmation
  const [deleteTarget, setDeleteTarget] = useState<UserRead | null>(null);

  // If no users, display fallback
  if (users.length === 0) {
    return <p className="users-empty">No users to display.</p>;
  }

  // Set variable that when activated will set selectred role to collapsed via switching boolean
  const toggle = (role: Role) =>
    setCollapsed(current => ({ ...current, [role]: !current[role] }));

  const handleConfirmDelete = async () => {
    if (!deleteTarget) return;
    try {
      await onDelete(deleteTarget.id);
    } catch (err) {
      console.debug("Delete failed:", err);
    }
    setDeleteTarget(null);
  };

  // Group the current page's users by role, keeping the order within each group
  const groups = ROLE_ORDER.map(role => ({
    role,
    members: users.filter(u => u.role === role),
  })).filter(group => group.members.length > 0);

  return (
    <>
      <div className="admin-table-wrapper">
        <table className="admin-species-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {groups.map(({ role, members }) => {
              const isCollapsed = collapsed[role];
              return (
                <Fragment key={role}>
                  <tr className="users-group-row">
                    <td colSpan={5}>
                      <button
                        type="button"
                        className="users-group-toggle"
                        aria-expanded={!isCollapsed}
                        onClick={() => toggle(role)}
                      >
                        <span
                          className={`users-group-caret${
                            isCollapsed ? " is-collapsed" : ""
                          }`}
                          aria-hidden="true"
                        >
                          ▾
                        </span>
                        {ROLE_LABELS[role]}
                        <span className="users-group-count">
                          ({members.length})
                        </span>
                      </button>
                    </td>
                  </tr>

                  {!isCollapsed &&
                    members.map(u => {
                      // Block role-change on your own row so an admin can't delete themselves
                      const isSelf = u.id === currentUserId;
                      return (
                        <tr
                          key={u.id}
                          className={isSelf ? "users-row-self" : ""}
                        >
                          <td>{u.name}</td>
                          <td>{u.email}</td>
                          <td>
                            <select
                              className="users-select"
                              value={u.role}
                              disabled={isMutating || isSelf}
                              title={
                                isSelf
                                  ? "You can't change your own role"
                                  : undefined
                              }
                              aria-label={`Role for ${u.name}`}
                              onChange={e =>
                                onChangeRole(u.id, e.target.value as Role)
                              }
                            >
                              {ROLES.map(role => (
                                <option key={role} value={role}>
                                  {ROLE_LABELS[role]}
                                </option>
                              ))}
                            </select>
                          </td>
                          <td>
                            <StatusBadge isApproved={u.is_approved} />
                          </td>
                          <td>
                            <button
                              type="button"
                              className="admin-action-btn admin-action-danger"
                              disabled={isMutating || isSelf}
                              title={
                                isSelf
                                  ? "You can't delete your own account"
                                  : undefined
                              }
                              onClick={() => setDeleteTarget(u)}
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {deleteTarget && (
        <ConfirmModal
          title="Delete User"
          message={
            <>
              Are you sure you want to delete{" "}
              <strong>{deleteTarget.name}</strong>? This action cannot be
              undone.
            </>
          }
          confirmLabel="Confirm Delete"
          pendingLabel="Deleting…"
          confirmIcon="🗑️"
          isPending={isMutating}
          onConfirm={handleConfirmDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </>
  );
}

function StatusBadge({ isApproved }: { isApproved: boolean | undefined }) {
  if (isApproved === undefined) {
    return <span className="users-badge users-badge-unknown">Unknown</span>;
  }
  return (
    <span
      className={[
        "users-badge",
        isApproved ? "users-badge-approved" : "users-badge-pending",
      ].join(" ")}
    >
      {isApproved ? "Approved" : "Pending"}
    </span>
  );
}
