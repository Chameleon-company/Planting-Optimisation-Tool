import { useState, useEffect } from "react";

export function useStickyHeader() {
  const [isScrolled, setIsScrolled] = useState(false);

  // UseEffect hook that triggers once on mount
  useEffect(() => {
    // Set header as topbar, if topbar does not exist, return
    const header = document.querySelector(".topbar") as HTMLElement | null;
    if (!header) return;

    // Toggle, if window has scrolled on the Y axis, then add is-scrolled to header
    const toggle = () => {
      if (window.scrollY > 4) {
        header.classList.add("is-scrolled");
        setIsScrolled(true);
      }
      // Otherwise remove is-scrolled from header
      else {
        header.classList.remove("is-scrolled");
        setIsScrolled(false);
      }
    };

    // Attach the toggle function to the window's scroll, trigger when scrolling happens
    // Call toggle once immediately on mount to set the correct initial state
    window.addEventListener("scroll", toggle, { passive: true });
    toggle();

    // Remove event listener when component unmounts
    return () => window.removeEventListener("scroll", toggle);
  }, []);

  // Return state if user has scrolled or not
  return { isScrolled };
}
