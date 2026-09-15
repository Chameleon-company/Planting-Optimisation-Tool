// @vitest-environment jsdom
import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import ConfirmModal from "@/components/shared/confirmModal";

const renderModal = (
  props: Partial<React.ComponentProps<typeof ConfirmModal>> = {}
) => {
  const onConfirm = vi.fn();
  const onCancel = vi.fn();
  const utils = render(
    <ConfirmModal
      title="Delete User"
      message="Are you sure? This cannot be undone."
      confirmLabel="Confirm Delete"
      isPending={false}
      onConfirm={onConfirm}
      onCancel={onCancel}
      {...props}
    />
  );
  return { onConfirm, onCancel, ...utils };
};

afterEach(() => {
  vi.restoreAllMocks();
});

describe("ConfirmModal", () => {
  it("renders the title, message, and both buttons", () => {
    renderModal();
    expect(screen.getByText("Delete User")).toBeInTheDocument();
    expect(
      screen.getByText(/are you sure\? this cannot be undone/i)
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /confirm delete/i })
    ).toBeInTheDocument();
  });

  it("renders a ReactNode message", () => {
    renderModal({
      message: (
        <>
          Reject <strong>Ada Lovelace</strong>?
        </>
      ),
    });
    const strong = screen.getByText("Ada Lovelace");
    expect(strong.tagName).toBe("STRONG");
  });

  it("fires onConfirm when the confirm button is clicked", async () => {
    const user = userEvent.setup();
    const { onConfirm, onCancel } = renderModal();
    await user.click(screen.getByRole("button", { name: /confirm delete/i }));
    expect(onConfirm).toHaveBeenCalledTimes(1);
    expect(onCancel).not.toHaveBeenCalled();
  });

  it("fires onCancel when the Cancel button is clicked", async () => {
    const user = userEvent.setup();
    const { onConfirm, onCancel } = renderModal();
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalledTimes(1);
    expect(onConfirm).not.toHaveBeenCalled();
  });

  it("fires onCancel when the backdrop is clicked", async () => {
    const user = userEvent.setup();
    const { onCancel } = renderModal();
    const backdrop = document.querySelector(
      ".confirm-modal-backdrop"
    ) as HTMLElement;
    await user.click(backdrop);
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("fires onCancel when ESC is pressed", () => {
    const { onCancel } = renderModal();
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
