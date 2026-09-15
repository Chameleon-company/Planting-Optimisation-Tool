import { useEffect } from "react";
import toast from "react-hot-toast";
import { Helmet } from "react-helmet-async";

import { useAuth } from "@/contexts/AuthContext";
import { useUsers } from "@/hooks/useUsers";

import PendingApprovals from "@/components/admin/userManagement/pendingApprovals";
import UsersTable from "@/components/admin/userManagement/usersTable";
import UsersPagination from "@/components/admin/userManagement/usersPagination";

import "@/components/admin/userManagement/users.css";

export default function AdminUsersPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const {
    users,
    pendingUsers,
    isLoading,
    isMutating,
    error,
    page,
    setPage,
    totalPages,
    totalUsers,
    updateUser,
    deleteUser,
    approveUser,
    rejectUser,
  } = useUsers();

  const pendingCount = pendingUsers.length;

  useEffect(() => {
    if (error) toast.error(error);
  }, [error]);

  // Page is admin-only, backup security
  if (!isAdmin) {
    return (
      <div className="users-view-container">
        <div className="users-error-message">
          <p>
            <strong>Access denied.</strong> This page is for administrators
            only.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="users-view-container">
      <Helmet>
        <title>User Management | Admin</title>
      </Helmet>

      {/* Table 1, all users grouped by role */}
      <section className="users-section">
        <div className="admin-species-header">
          <div>
            <h2>All Users</h2>
            <p>Change a users role or remove their account.</p>
            <p className="users-subtitle">
              {totalUsers} {totalUsers === 1 ? "user" : "users"}
              {pendingCount > 0 && (
                <>
                  {" · "}
                  <span className="users-pending-flag">
                    {pendingCount} awaiting approval
                  </span>
                </>
              )}
            </p>
          </div>
        </div>

        {isLoading ? (
          <p className="users-empty">Loading users…</p>
        ) : (
          <>
            <UsersTable
              users={users}
              currentUserId={user?.id ?? null}
              isMutating={isMutating}
              onChangeRole={(id, role) => updateUser(id, { role })}
              onDelete={deleteUser}
            />
            <UsersPagination
              page={page}
              totalPages={totalPages}
              onPageChange={setPage}
            />
          </>
        )}
      </section>

      {/* Table 2, pending queue */}
      <PendingApprovals
        pending={pendingUsers}
        isMutating={isMutating}
        onApprove={approveUser}
        onReject={rejectUser}
      />
    </div>
  );
}
