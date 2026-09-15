import { useState } from "react";
import { ROLES, ROLE_LABELS, type Role, type UserRead } from "@/utils/usersAPI";
import ConfirmModal from "@/components/shared/confirmModal";
import "./users.css";

// Pending accounts are of UserRead type from backend
// IsMutating boolean to disable buttons if already pressed elsewhere
// OnApprove requiring ID and Role and promising a return, handing back up to usersTable
// and then UsersPage, before being handed to API call, same with onReject
interface Props {
  pending: UserRead[];
  isMutating: boolean;
  onApprove: (userId: number, role: Role) => Promise<unknown>;
  onReject: (userId: number) => Promise<unknown>;
}

export default function PendingApprovals({
  pending,
  isMutating,
  onApprove,
  onReject,
}: Props) {
  const hasPending = pending.length > 0;

  return (
    <section className="users-section">
      <div className="admin-species-header">
        <div>
          <h2>Pending Approvals</h2>
          <p>Review new registrations and assign each an effective role.</p>
        </div>
        {hasPending && (
          <span className="users-count-badge">{pending.length}</span>
        )}
      </div>

      {!hasPending ? (
        <p className="users-empty">No accounts are waiting for approval.</p>
      ) : (
        <div className="admin-table-wrapper">
          <table className="admin-species-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Requested</th>
                <th>Assign role</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pending.map(applicant => (
                <PendingRow
                  key={applicant.id}
                  applicant={applicant}
                  isMutating={isMutating}
                  onApprove={onApprove}
                  onReject={onReject}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

interface RowProps {
  applicant: UserRead;
  isMutating: boolean;
  onApprove: (userId: number, role: Role) => Promise<unknown>;
  onReject: (userId: number) => Promise<unknown>;
}

// Each row has the role the admin is about to assign, defaulting to what the applicant requested
function PendingRow({ applicant, isMutating, onApprove, onReject }: RowProps) {
  const [effectiveRole, setEffectiveRole] = useState<Role>(
    applicant.requested_role ?? ROLES[0]
  );

  // The row awaiting reject confirmation
  const [confirmReject, setConfirmReject] = useState(false);

  const handleConfirmReject = async () => {
    try {
      await onReject(applicant.id);
    } catch (err) {
      console.debug("Reject failed:", err);
    }
    setConfirmReject(false);
  };

  return (
    <tr>
      <td>{applicant.name}</td>
      <td>{applicant.email}</td>
      <td>
        {applicant.requested_role ? ROLE_LABELS[applicant.requested_role] : "-"}
      </td>
      <td>
        <select
          className="users-select"
          value={effectiveRole}
          disabled={isMutating}
          aria-label={`Assign role for ${applicant.name}`}
          onChange={e => setEffectiveRole(e.target.value as Role)}
        >
          {ROLES.map(role => (
            <option key={role} value={role}>
              {ROLE_LABELS[role]}
            </option>
          ))}
        </select>
      </td>
      <td>
        <button
          type="button"
          className="admin-action-btn"
          disabled={isMutating}
          onClick={() => onApprove(applicant.id, effectiveRole).catch(() => {})}
        >
          Approve
        </button>
        <button
          type="button"
          className="admin-action-btn admin-action-danger"
          disabled={isMutating}
          onClick={() => setConfirmReject(true)}
        >
          Reject
        </button>
      </td>

      {confirmReject && (
        <ConfirmModal
          title="Reject Registration"
          message={
            <>
              Are you sure you want to reject <strong>{applicant.name}</strong>?
              This permanently removes their pending registration and cannot be
              undone.
            </>
          }
          confirmLabel="Confirm Reject"
          pendingLabel="Rejecting…"
          confirmIcon="🚫"
          isPending={isMutating}
          onConfirm={handleConfirmReject}
          onCancel={() => setConfirmReject(false)}
        />
      )}
    </tr>
  );
}
