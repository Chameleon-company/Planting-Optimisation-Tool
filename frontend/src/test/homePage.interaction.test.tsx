// @vitest-environment jsdom

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";

import HomePage from "../pages/HomePage";

describe("HomePage interactions", () => {
  it("navigates to profile page when clicking 'Generate environmental profile'", async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/profile" element={<div>Profile Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    // Find clickable element (text or button inside card)
    const card = screen.getByRole("link", {
      name: /generate environmental profile/i,
    });

    await user.click(card);

    // Assert navigation happened
    expect(screen.getByText("Profile Page")).toBeInTheDocument();
  });

  it("does not navigate when clicking non-clickable area", async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/profile" element={<div>Profile Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    // Click a non-interactive area of the page
    await user.click(document.body);

    // Expect navigation to not have occurred
    expect(screen.queryByText("Profile Page")).not.toBeInTheDocument();
  });
});
