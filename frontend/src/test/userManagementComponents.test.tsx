import { describe, it, expect, vi } from "vitest";
import { render, screen, within, waitFor } from "@testing-library/react";
import UserEvent from "@testing-library/user-event";

import UsersTable from "@/components/admin/userManagement/usersTable";
import PendingApprovals from "@/components/admin/userManagement/pendingApprovals";
import UsersPagination from "@/components/admin/userManagement/usersPagination";
import type { UserRead } from "@/utils/usersAPI";

const makeUser = (
  id: number,
  role: UserRead["role"],
  overrides: Partial<UserRead> = {}
): UserRead => ({
  id,
  role,
  name: `User ${id}`,
  email: `user${id}@example.com`,
  is_approved: true,
  requested_role: null,
  ...overrides,
});

// UsersTable

describe("UsersTable", () => {
  const noop = vi.fn();

  it("renders a fallback when there are no users", () => {
    render(
      <UsersTable
        users={[]}
        currentUserId={null}
        isMutating={false}
        onChangeRole={noop}
        onDelete={vi.fn().mockResolvedValue(undefined)}
      />
    );

    expect(screen.getByText(/no users to display/i)).toBeInTheDocument();
  });

  it("groups users by rank with a per-group count", () => {
    render(
      <UsersTable
        users={[
          makeUser(1, "admin", { name: "Ada" }),
          makeUser(2, "supervisor", { name: "Sam" }),
          makeUser(3, "officer", { name: "Ori" }),
        ]}
        currentUserId={null}
        isMutating={false}
        onChangeRole={noop}
        onDelete={vi.fn().mockResolvedValue(undefined)}
      />
    );

    expect(
      screen.getByRole("button", { name: /admin\s*\(1\)/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /supervisor\s*\(1\)/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /officer\s*\(1\)/i })
    ).toBeInTheDocument();
  });

  it("hides a group's members when its header is collapsed", async () => {
    const user = UserEvent.setup();
    render(
      <UsersTable
        users={[makeUser(1, "admin", { name: "Ada" })]}
        currentUserId={null}
        isMutating={false}
        onChangeRole={noop}
        onDelete={vi.fn().mockResolvedValue(undefined)}
      />
    );

    expect(screen.getByText("Ada")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /admin\s*\(1\)/i }));

    expect(screen.queryByText("Ada")).not.toBeInTheDocument();
  });

  it("masks the name with a placeholder when the backend omits it", () => {
    render(
      <UsersTable
        users={[makeUser(5, "officer", { name: null })]}
        currentUserId={null}
        isMutating={false}
        onChangeRole={vi.fn()}
        onDelete={vi.fn().mockResolvedValue(undefined)}
      />
    );

    expect(screen.getByText("******")).toBeInTheDocument();
    expect(screen.queryByText("User 5")).not.toBeInTheDocument();
  });

  it("calls onChangeRole with the new role when the select changes", async () => {
    const user = UserEvent.setup();
    const onChangeRole = vi.fn();

    render(
      <UsersTable
        users={[makeUser(2, "officer", { name: "Bob" })]}
        currentUserId={null}
        isMutating={false}
        onChangeRole={onChangeRole}
        onDelete={vi.fn().mockResolvedValue(undefined)}
      />
    );

    await user.selectOptions(
      screen.getByLabelText(/role for user2@example\.com/i),
      "supervisor"
    );

    expect(onChangeRole).toHaveBeenCalledWith(2, "supervisor");
  });

  it("disables the role select and delete button on your own row", () => {
    const { container } = render(
      <UsersTable
        users={[makeUser(99, "admin", { name: "Me" })]}
        currentUserId={99}
        isMutating={false}
        onChangeRole={noop}
        onDelete={vi.fn().mockResolvedValue(undefined)}
      />
    );

    const selfRow = container.querySelector("tr.users-row-self") as HTMLElement;
    expect(selfRow).not.toBeNull();
    expect(
      within(selfRow).getByLabelText(/role for user99@example\.com/i)
    ).toBeDisabled();
    expect(
      within(selfRow).getByRole("button", { name: /delete/i })
    ).toBeDisabled();
  });

  it("disables role/delete controls while a mutation is in flight", () => {
    render(
      <UsersTable
        users={[makeUser(2, "officer", { name: "Bob" })]}
        currentUserId={null}
        isMutating={true}
        onChangeRole={noop}
        onDelete={vi.fn().mockResolvedValue(undefined)}
      />
    );

    expect(
      screen.getByLabelText(/role for user2@example\.com/i)
    ).toBeDisabled();
    expect(screen.getByRole("button", { name: /delete/i })).toBeDisabled();
  });

  describe("delete confirmation modal", () => {
    it("opens the modal, confirms, and calls onDelete with the id", async () => {
      const user = UserEvent.setup();
      const onDelete = vi.fn().mockResolvedValue(undefined);

      render(
        <UsersTable
          users={[makeUser(2, "officer", { name: "Bob" })]}
          currentUserId={null}
          isMutating={false}
          onChangeRole={vi.fn()}
          onDelete={onDelete}
        />
      );

      await user.click(screen.getByRole("button", { name: /delete/i }));

      const dialog = screen.getByRole("dialog");
      expect(within(dialog).getByText(/delete user/i)).toBeInTheDocument();
      expect(within(dialog).getByText("user2@example.com")).toBeInTheDocument();

      await user.click(
        within(dialog).getByRole("button", { name: /confirm delete/i })
      );

      expect(onDelete).toHaveBeenCalledWith(2);
      await waitFor(() =>
        expect(screen.queryByRole("dialog")).not.toBeInTheDocument()
      );
    });

    it("closes without deleting when Cancel is clicked", async () => {
      const user = UserEvent.setup();
      const onDelete = vi.fn().mockResolvedValue(undefined);

      render(
        <UsersTable
          users={[makeUser(2, "officer", { name: "Bob" })]}
          currentUserId={null}
          isMutating={false}
          onChangeRole={vi.fn()}
          onDelete={onDelete}
        />
      );

      await user.click(screen.getByRole("button", { name: /delete/i }));
      await user.click(screen.getByRole("button", { name: /cancel/i }));

      expect(onDelete).not.toHaveBeenCalled();
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });

    it("closes the modal when Escape is pressed", async () => {
      const user = UserEvent.setup();

      render(
        <UsersTable
          users={[makeUser(2, "officer", { name: "Bob" })]}
          currentUserId={null}
          isMutating={false}
          onChangeRole={vi.fn()}
          onDelete={vi.fn().mockResolvedValue(undefined)}
        />
      );

      await user.click(screen.getByRole("button", { name: /delete/i }));
      expect(screen.getByRole("dialog")).toBeInTheDocument();

      await user.keyboard("{Escape}");

      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });

  describe("StatusBadge", () => {
    it("labels approved and pending users", () => {
      render(
        <UsersTable
          users={[
            makeUser(1, "officer", { name: "Yes", is_approved: true }),
            makeUser(2, "officer", { name: "No", is_approved: false }),
          ]}
          currentUserId={null}
          isMutating={false}
          onChangeRole={vi.fn()}
          onDelete={vi.fn().mockResolvedValue(undefined)}
        />
      );

      expect(screen.getByText("Approved")).toBeInTheDocument();
      expect(screen.getByText("Pending")).toBeInTheDocument();
    });
  });
});

// PendingApprovals

describe("PendingApprovals", () => {
  const applicant = (id: number, overrides: Partial<UserRead> = {}): UserRead =>
    makeUser(id, "officer", { is_approved: false, ...overrides });

  it("shows a fallback and no badge when the queue is empty", () => {
    render(
      <PendingApprovals
        pending={[]}
        isMutating={false}
        onApprove={vi.fn().mockResolvedValue(undefined)}
        onReject={vi.fn().mockResolvedValue(undefined)}
      />
    );

    expect(
      screen.getByText(/no accounts are waiting for approval/i)
    ).toBeInTheDocument();
    expect(screen.queryByText("0")).not.toBeInTheDocument();
  });

  it("shows the requested role, or a dash when none was requested", () => {
    render(
      <PendingApprovals
        pending={[
          applicant(1, { name: "Ann", requested_role: "supervisor" }),
          applicant(2, { name: "Ben", requested_role: null }),
        ]}
        isMutating={false}
        onApprove={vi.fn().mockResolvedValue(undefined)}
        onReject={vi.fn().mockResolvedValue(undefined)}
      />
    );

    const annRow = screen.getByText("Ann").closest("tr") as HTMLElement;
    const benRow = screen.getByText("Ben").closest("tr") as HTMLElement;

    expect(within(annRow).getAllByRole("cell")[2]).toHaveTextContent(
      "Supervisor"
    );
    expect(within(benRow).getAllByRole("cell")[2]).toHaveTextContent("-");
  });

  it("defaults the assign-role select to the requested role, else the lowest role", () => {
    render(
      <PendingApprovals
        pending={[
          applicant(1, { name: "Ann", requested_role: "supervisor" }),
          applicant(2, { name: "Ben", requested_role: null }),
        ]}
        isMutating={false}
        onApprove={vi.fn().mockResolvedValue(undefined)}
        onReject={vi.fn().mockResolvedValue(undefined)}
      />
    );

    expect(
      screen.getByLabelText(/assign role for user1@example\.com/i)
    ).toHaveValue("supervisor");
    expect(
      screen.getByLabelText(/assign role for user2@example\.com/i)
    ).toHaveValue("officer");
  });

  it("approves with the requested role by default", async () => {
    const user = UserEvent.setup();
    const onApprove = vi.fn().mockResolvedValue(undefined);

    render(
      <PendingApprovals
        pending={[applicant(1, { name: "Ann", requested_role: "supervisor" })]}
        isMutating={false}
        onApprove={onApprove}
        onReject={vi.fn().mockResolvedValue(undefined)}
      />
    );

    await user.click(screen.getByRole("button", { name: /approve/i }));

    expect(onApprove).toHaveBeenCalledWith(1, "supervisor");
  });

  it("approves with an overridden role after changing the select", async () => {
    const user = UserEvent.setup();
    const onApprove = vi.fn().mockResolvedValue(undefined);

    render(
      <PendingApprovals
        pending={[applicant(1, { name: "Ann", requested_role: "supervisor" })]}
        isMutating={false}
        onApprove={onApprove}
        onReject={vi.fn().mockResolvedValue(undefined)}
      />
    );

    await user.selectOptions(
      screen.getByLabelText(/assign role for user1@example\.com/i),
      "admin"
    );
    await user.click(screen.getByRole("button", { name: /approve/i }));

    expect(onApprove).toHaveBeenCalledWith(1, "admin");
  });

  describe("reject confirmation modal", () => {
    it("opens the modal, confirms, and calls onReject with the id", async () => {
      const user = UserEvent.setup();
      const onReject = vi.fn().mockResolvedValue(undefined);

      render(
        <PendingApprovals
          pending={[applicant(1, { name: "Ann" })]}
          isMutating={false}
          onApprove={vi.fn().mockResolvedValue(undefined)}
          onReject={onReject}
        />
      );

      await user.click(screen.getByRole("button", { name: "Reject" }));

      const dialog = screen.getByRole("dialog");
      expect(
        within(dialog).getByText(/reject registration/i)
      ).toBeInTheDocument();
      expect(within(dialog).getByText("user1@example.com")).toBeInTheDocument();

      await user.click(
        within(dialog).getByRole("button", { name: /confirm reject/i })
      );

      expect(onReject).toHaveBeenCalledWith(1);
      await waitFor(() =>
        expect(screen.queryByRole("dialog")).not.toBeInTheDocument()
      );
    });

    it("closes without rejecting when Cancel is clicked", async () => {
      const user = UserEvent.setup();
      const onReject = vi.fn().mockResolvedValue(undefined);

      render(
        <PendingApprovals
          pending={[applicant(1, { name: "Ann" })]}
          isMutating={false}
          onApprove={vi.fn().mockResolvedValue(undefined)}
          onReject={onReject}
        />
      );

      await user.click(screen.getByRole("button", { name: "Reject" }));
      await user.click(screen.getByRole("button", { name: /cancel/i }));

      expect(onReject).not.toHaveBeenCalled();
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });

    it("closes without rejecting when Escape is pressed", async () => {
      const user = UserEvent.setup();
      const onReject = vi.fn().mockResolvedValue(undefined);

      render(
        <PendingApprovals
          pending={[applicant(1, { name: "Ann" })]}
          isMutating={false}
          onApprove={vi.fn().mockResolvedValue(undefined)}
          onReject={onReject}
        />
      );

      await user.click(screen.getByRole("button", { name: "Reject" }));
      expect(screen.getByRole("dialog")).toBeInTheDocument();

      await user.keyboard("{Escape}");

      expect(onReject).not.toHaveBeenCalled();
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });

  it("disables Approve and Reject while a mutation is in flight", () => {
    render(
      <PendingApprovals
        pending={[applicant(1, { name: "Ann" })]}
        isMutating={true}
        onApprove={vi.fn().mockResolvedValue(undefined)}
        onReject={vi.fn().mockResolvedValue(undefined)}
      />
    );

    expect(screen.getByRole("button", { name: /approve/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Reject" })).toBeDisabled();
  });
});

// UsersPagination

describe("UsersPagination", () => {
  it("renders nothing for a single page", () => {
    const { container } = render(
      <UsersPagination page={0} totalPages={1} onPageChange={vi.fn()} />
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("renders nothing when there are no pages", () => {
    const { container } = render(
      <UsersPagination page={0} totalPages={0} onPageChange={vi.fn()} />
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("shows the current page indicator and disables Prev on the first page", () => {
    const { container } = render(
      <UsersPagination page={0} totalPages={3} onPageChange={vi.fn()} />
    );

    expect(container.querySelector(".users-page-indicator")?.textContent).toBe(
      "Page 1 of 3"
    );
    expect(screen.getByRole("button", { name: /prev/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /next/i })).toBeEnabled();
  });

  it("disables Next on the last page", () => {
    render(<UsersPagination page={2} totalPages={3} onPageChange={vi.fn()} />);

    expect(screen.getByRole("button", { name: /next/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /prev/i })).toBeEnabled();
  });
});
