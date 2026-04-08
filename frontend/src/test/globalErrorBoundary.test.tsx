import { it, expect, describe } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import UserEvent from "@testing-library/user-event";

import GlobalErrorBoundary from "../errors/GlobalErrorBoundary";

// Create mock error following JSON template of detail, error: [field, message]
const ThrowError = () => {
  throw {
    detail: "Invalid Input",
    errors: [
      { field: "Field1", message: "Error" },
      { field: "Field2", message: "Error" },
      { field: "Field3", message: "Error" },
    ],
  };
};

// Create mock error without any fields
const ThrowErrorNoFields = () => {
  throw {};
};

describe("GlobalErrorBoundary", () => {
  it("should render children when no error is detected", () => {
    // Render children within ErrorBoundary
    render(
      <GlobalErrorBoundary>
        <p>All good</p>
      </GlobalErrorBoundary>
    );

    // Expect children of ErrorBoundary to appear if no error is spotted
    expect(screen.getByText("All good")).toBeInTheDocument();
  });

  it("should show fallback UI when any error is detected", async () => {
    // Render ThrowError within ErrorBoundary
    render(
      <GlobalErrorBoundary>
        <ThrowError />
      </GlobalErrorBoundary>
    );

    // Expect ErrorBoundary Fallback UI to take priority if an error is detected
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("should show detailed message when thrown", async () => {
    // Render ThrowError within ErrorBoundary
    const { container } = render(
      <GlobalErrorBoundary>
        <ThrowError />
      </GlobalErrorBoundary>
    );

    // Expect ErrorBoundary to display Fallback UI text
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    expect(screen.getByText("Invalid Input")).toBeInTheDocument();

    // Expect ErrorBoundary to display fields given by error within Fallback UI
    const items = container.querySelectorAll("li");
    expect(items.length).toBe(3);
    expect(items[0].textContent).toContain("Field1");
    expect(items[1].textContent).toContain("Field2");
    expect(items[2].textContent).toContain("Field3");
  });

  it("should not show field errors if no field errors are given", () => {
    // Render ThrowErrorNoFields within ErrorBoundary
    const { container } = render(
      <GlobalErrorBoundary>
        <ThrowErrorNoFields />
      </GlobalErrorBoundary>
    );

    // Expect ErrorBoundary to display Fallback UI without any fields
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    expect(container.querySelector("ul")).not.toBeInTheDocument();
  });

  it("should reset and render children when Try again is clicked", async () => {
    // Create fake user
    const user = UserEvent.setup();

    // Create flexible boolean
    let shouldThrow = true;

    // Create function, if shouldThrow is true, throw, if false, do not throw
    const MaybeThrow = () => {
      if (shouldThrow) throw new Error("Test error");
      return <p>Recovered</p>;
    };

    // Render MaybeThrow in GlobalErrorBoundary
    render(
      <GlobalErrorBoundary>
        <MaybeThrow />
      </GlobalErrorBoundary>
    );

    // Expect Fallback UI to appear
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();

    // Set boolean to false
    shouldThrow = false;

    // Await user to click 'try again' button
    await user.click(screen.getByRole("button", { name: /try again/i }));

    // Await waitFor function until timeout or expect 'Recovered' from MaybeThrow to appear in document
    await waitFor(() => {
      expect(screen.getByText("Recovered")).toBeInTheDocument();
    });
  });
});
