import "./style.css";
import "./home.css";

// Nav Logic
export function initNav() {
  const path = window.location.pathname;
  let page = "home";
  if (path.includes("profile.html")) page = "profile";
  else if (path.includes("calculator.html")) page = "calculator";
  else if (path.includes("species.html")) page = "species";

  const links = document.querySelectorAll(".nav .nav-link");
  links.forEach(el => {
    const link = el as HTMLAnchorElement;
    const pageId = link.dataset.page;
    if (pageId === page) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
}

// Sticky Header Logic
export function initStickyHeader() {
  const header = document.querySelector(".topbar") as HTMLElement | null;
  if (!header) return;
  const toggle = () => {
    if (window.scrollY > 4) header.classList.add("is-scrolled");
    else header.classList.remove("is-scrolled");
  };
  window.addEventListener("scroll", toggle, {
    passive: true,
  } as AddEventListenerOptions);
  toggle();
}

// Initialisation
if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    initNav();
    initStickyHeader();
  });
}
