// @vitest-environment jsdom

import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";

// Hook to test
import { useStickyHeader } from "@/hooks/useStickyHeader";

describe("useStickyHeader Hook", () => {
  beforeEach(() => {
    document.body.innerHTML = "";
    // Reset scroll to top before each test
    Object.defineProperty(window, "scrollY", { value: 0, writable: true });
  });

  it("adds 'is-scrolled' class and returns isScrolled true when scrolling down", () => {
    // Create header element
    document.body.innerHTML = `<header class="topbar"></header>`;
    const header = document.querySelector(".topbar");

    const { result } = renderHook(() => useStickyHeader());

    // Simulate scroll
    act(() => {
      Object.defineProperty(window, "scrollY", { value: 100, writable: true });
      window.dispatchEvent(new Event("scroll"));
    });

    // Check DOM class
    expect(header?.classList.contains("is-scrolled")).toBe(true);
    // Check hook return value
    expect(result.current.isScrolled).toBe(true);
  });

  it("removes 'is-scrolled' class and returns isScrolled false when back at top", () => {
    document.body.innerHTML = `<header class="topbar is-scrolled"></header>`;
    const header = document.querySelector(".topbar");

    const { result } = renderHook(() => useStickyHeader());

    // Scroll down first
    act(() => {
      Object.defineProperty(window, "scrollY", { value: 100, writable: true });
      window.dispatchEvent(new Event("scroll"));
    });

    // Scroll back to top
    act(() => {
      Object.defineProperty(window, "scrollY", { value: 0, writable: true });
      window.dispatchEvent(new Event("scroll"));
    });

    // Check DOM class
    expect(header?.classList.contains("is-scrolled")).toBe(false);
    // Check hook return value
    expect(result.current.isScrolled).toBe(false);
  });

  it("returns isScrolled false on initial render when not scrolled", () => {
    document.body.innerHTML = `<header class="topbar"></header>`;

    const { result } = renderHook(() => useStickyHeader());

    expect(result.current.isScrolled).toBe(false);
  });

  it("returns isScrolled true immediately on mount if page is already scrolled", () => {
    document.body.innerHTML = `<header class="topbar"></header>`;

    // Simulate page already scrolled before hook mounts
    Object.defineProperty(window, "scrollY", { value: 100, writable: true });

    const { result } = renderHook(() => useStickyHeader());

    expect(result.current.isScrolled).toBe(true);
  });

  it("does not throw error if header element is missing", () => {
    expect(() => {
      renderHook(() => useStickyHeader());

      act(() => {
        Object.defineProperty(window, "scrollY", { value: 50, writable: true });
        window.dispatchEvent(new Event("scroll"));
      });
    }).not.toThrow();
  });
});
