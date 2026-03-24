import { useState, useEffect } from "react";

export function useStickyHeader() {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const header = document.querySelector(".topbar") as HTMLElement | null;
    if (!header) return;

    const toggle = () => {
      if (window.scrollY > 4) {
        header.classList.add("is-scrolled");
        setIsScrolled(true);
      } else {
        header.classList.remove("is-scrolled");
        setIsScrolled(false);
      }
    };

    window.addEventListener("scroll", toggle, { passive: true });
    toggle();

    return () => window.removeEventListener("scroll", toggle);
  }, []);

  return { isScrolled };
}
