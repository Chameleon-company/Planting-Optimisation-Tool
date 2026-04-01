import { it, expect, describe } from "vitest";
import { render } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";

import MainLayout from "../components/layout/layout";

// Create mock layout render wrapping mock Home page
const renderWithRouter = () => {
  return render(
    <MemoryRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route index element={<div>Home</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
};

describe("MainLayout", () => {
  it("should render the nav and footer", () => {
    // Render MainLayout component
    const { container } = renderWithRouter();

    // Expect Nav and Footer components are available
    expect(container.querySelector(".topbar")).toBeInTheDocument();
    expect(container.querySelector(".site-footer")).toBeInTheDocument();
  });

  it("should add is-scrolled class when scrolled down", () => {
    // Render MainLayout component
    const { container } = renderWithRouter();

    // Pretend to scroll down 100 pixels
    Object.defineProperty(window, "scrollY", { value: 100, writable: true });
    window.dispatchEvent(new Event("scroll"));

    // Expect Nav component to become '.topbar.is-scrolled' from '.topbar'
    expect(container.querySelector(".topbar.is-scrolled")).toBeInTheDocument();
  });

  it("should remove is-scrolled class when back at top", () => {
    // Render MainLayout component
    const { container } = renderWithRouter();

    // Pretend to scroll down 100 pixels
    Object.defineProperty(window, "scrollY", { value: 100, writable: true });
    window.dispatchEvent(new Event("scroll"));

    // Pretend to scroll up 100 pixels
    Object.defineProperty(window, "scrollY", { value: 0, writable: true });
    window.dispatchEvent(new Event("scroll"));

    // Expect '.topbar' to have removed '.is-scrolled' from className
    expect(
      container.querySelector(".topbar.is-scrolled")
    ).not.toBeInTheDocument();
  });
});
