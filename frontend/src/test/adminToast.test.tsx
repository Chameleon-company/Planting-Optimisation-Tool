import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import AdminToast from "@/components/admin/AdminToast";

describe("AdminToast", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders a success notification", () => {
    render(
      <AdminToast
        message="Rule saved successfully."
        type="success"
        onClose={vi.fn()}
        durationMs={0}
      />
    );

    expect(screen.getByRole("status")).toHaveTextContent(
      "Rule saved successfully."
    );
  });

  it("renders an error notification", () => {
    render(
      <AdminToast
        message="Failed to save rule."
        type="error"
        onClose={vi.fn()}
        durationMs={0}
      />
    );

    expect(screen.getByRole("alert")).toHaveTextContent("Failed to save rule.");
  });

  it("closes when the dismiss button is clicked", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    render(
      <AdminToast
        message="Rule saved successfully."
        type="success"
        onClose={onClose}
        durationMs={0}
      />
    );

    await user.click(
      screen.getByRole("button", {
        name: /dismiss notification/i,
      })
    );

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("automatically closes after the configured duration", () => {
    vi.useFakeTimers();

    const onClose = vi.fn();

    render(
      <AdminToast
        message="Rule saved successfully."
        type="success"
        onClose={onClose}
        durationMs={2000}
      />
    );

    expect(onClose).not.toHaveBeenCalled();

    vi.advanceTimersByTime(2000);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("does not start an auto-close timer when duration is disabled", () => {
    vi.useFakeTimers();

    const onClose = vi.fn();

    render(
      <AdminToast
        message="Rule saved successfully."
        type="success"
        onClose={onClose}
        durationMs={0}
      />
    );

    vi.runAllTimers();

    expect(onClose).not.toHaveBeenCalled();
  });
});
