// @vitest-environment jsdom
import { describe, expect, it, beforeEach, vi } from "vitest";
import { initNav, initStickyHeader } from "../src/home";

describe("Home Page Logic", () => {
  beforeEach(() => {
    document.body.innerHTML = "";
    vi.restoreAllMocks();
  });

  describe("initNav", () => {
    it("should set the 'home' link to active when on the index page", () => {
      // Pretend on the homepage
      Object.defineProperty(window, "location", {
        value: { pathname: "/index.html" },
        writable: true,
      });

      // Create the fake HTML for the navbar
      document.body.innerHTML = `
        <nav class="nav">
          <a href="/index.html" class="nav-link" data-page="home">Home</a>
          <a href="/species.html" class="nav-link" data-page="species">Species</a>
        </nav>
      `;

      initNav();

      // Check if the class was added
      const homeLink = document.querySelector('[data-page="home"]');
      expect(homeLink?.classList.contains("active")).toBe(true);
    });

    it("should remove active class from home if we are on the species page", () => {
      // Pretend on the species page
      Object.defineProperty(window, "location", {
        value: { pathname: "/species.html" },
        writable: true,
      });

      // Create HTML where Home is already active
      document.body.innerHTML = `
        <nav class="nav">
          <a href="/index.html" class="nav-link active" data-page="home">Home</a>
          <a href="/species.html" class="nav-link" data-page="species">Species</a>
        </nav>
      `;

      initNav();

      const homeLink = document.querySelector('[data-page="home"]');

      expect(homeLink?.classList.contains("active")).toBe(false);
    });
  });

  describe("initStickyHeader", () => {
    it("should add 'is-scrolled' class when scrolling down", () => {
      // Create the header element
      document.body.innerHTML = `<header class="topbar">Header</header>`;
      const header = document.querySelector(".topbar");

      initStickyHeader();

      // Pretend to scroll down 100 pixels
      Object.defineProperty(window, "scrollY", { value: 100, writable: true });
      window.dispatchEvent(new Event("scroll"));

      expect(header?.classList.contains("is-scrolled")).toBe(true);
    });

    it("should remove 'is-scrolled' class when scrolling back to top", () => {
      // Create header that is already scrolled
      document.body.innerHTML = `<header class="topbar is-scrolled">Header</header>`;
      const header = document.querySelector(".topbar");

      initStickyHeader();

      // Pretend to scroll back to top
      Object.defineProperty(window, "scrollY", { value: 0, writable: true });
      window.dispatchEvent(new Event("scroll"));

      expect(header?.classList.contains("is-scrolled")).toBe(false);
    });
  });
});
