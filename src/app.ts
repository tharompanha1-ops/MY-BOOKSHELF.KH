/**
 * MY BOOKSHELF — Shared site behavior (TypeScript).
 *
 * Compiled to a classic script (assets/js/app.js) and loaded by every
 * page via <script src="assets/js/app.js" defer>.
 *
 * Handles: footer reveal, mobile navigation, theme toggle, active-link
 * highlighting, a toast helper, and a broken-link detector that reports
 * only — it never rewrites or removes any link.
 */

interface Window {
  showToast: (message: string, ms?: number) => void;
}

(function () {
  "use strict";

  /* ---------------- DOM helpers ---------------- */
  const $ = (id: string): HTMLElement | null => document.getElementById(id);

  /* ---------------- Footer scroll-reveal ---------------- */
  function initFooterReveal(): void {
    const footerEl: HTMLElement | null = document.querySelector(
      ".site-footer, .footer",
    );
    if (!footerEl) return;
    if (!("IntersectionObserver" in window)) {
      footerEl.classList.add("in-view");
      return;
    }
    const observer = new IntersectionObserver(
      (entries: IntersectionObserverEntry[]) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            footerEl.classList.add("in-view");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 },
    );
    observer.observe(footerEl);
  }

  /* ---------------- Mobile navigation ---------------- */
  function initNav(): void {
    const menuToggle = $("menuToggle");
    const navMenu = $("navMenu") ?? document.querySelector(".main-nav");
    if (menuToggle && navMenu) {
      menuToggle.addEventListener("click", () => {
        const open = navMenu.classList.toggle("active");
        menuToggle.setAttribute("aria-expanded", String(open));
        const icon = menuToggle.querySelector("i");
        if (icon) {
          icon.classList.toggle("fa-bars", !open);
          icon.classList.toggle("fa-xmark", open);
        }
      });
      navMenu.querySelectorAll("a").forEach((a) =>
        a.addEventListener("click", () => {
          navMenu.classList.remove("active");
          menuToggle.setAttribute("aria-expanded", "false");
          const icon = menuToggle.querySelector("i");
          if (icon) {
            icon.classList.add("fa-bars");
            icon.classList.remove("fa-xmark");
          }
        }),
      );
    }

    const iconToggle = $("iconToggle");
    const iconLinks = $("iconLinks");
    if (iconToggle && iconLinks) {
      iconToggle.addEventListener("click", () => {
        const open = iconLinks.classList.toggle("active");
        iconToggle.setAttribute("aria-expanded", String(open));
        const icon = iconToggle.querySelector("i");
        if (icon) {
          icon.classList.toggle("fa-toolbox", !open);
          icon.classList.toggle("fa-xmark", open);
        }
      });
    }

    // Close menus when resizing back to desktop
    window.addEventListener("resize", () => {
      if (window.innerWidth > 860) {
        [navMenu, iconLinks].forEach((el) => el && el.classList.remove("active"));
      }
    });
  }

  /* ---------------- Toast ---------------- */
  function getToast(): HTMLElement {
    let toast = $("downloadToast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "downloadToast";
      document.body.appendChild(toast);
    }
    return toast;
  }
  function showToast(message: string, ms?: number): void {
    const toast = getToast();
    toast.textContent = message;
    toast.classList.add("show");
    const hideTimer = (toast as HTMLElement & { _hideTimer?: number })._hideTimer;
    if (hideTimer) window.clearTimeout(hideTimer);
    (toast as HTMLElement & { _hideTimer?: number })._hideTimer =
      window.setTimeout(() => toast.classList.remove("show"), ms ?? 2600);
  }
  window.showToast = showToast;

  /* ---------------- Theme toggle ---------------- */
  function initTheme(): void {
    const root = document.documentElement;
    const stored = localStorage.getItem("mb-theme");
    if (stored) root.setAttribute("data-theme", stored);

    const toggle = $("themeToggle");
    if (!toggle) return;

    const isDark = (): boolean =>
      root.getAttribute("data-theme") === "dark" ||
      (root.getAttribute("data-theme") !== "light" &&
        window.matchMedia("(prefers-color-scheme: dark)").matches);

    const syncLabel = (): void => {
      const icon = toggle.querySelector("i");
      if (icon) {
        icon.className = isDark() ? "fas fa-sun" : "fas fa-moon";
      }
      const label = isDark() ? "Switch to light mode" : "Switch to dark mode";
      toggle.setAttribute("aria-label", label);
      toggle.setAttribute("title", label);
    };
    syncLabel();
    toggle.addEventListener("click", () => {
      const next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      localStorage.setItem("mb-theme", next);
      syncLabel();
    });
  }

  /* ---------------- Active nav highlighting ---------------- */
  function initActiveNav(): void {
    const here = location.pathname.split("/").pop() || "index.html";
    document
      .querySelectorAll<HTMLAnchorElement>(".main-nav a, nav ul li a")
      .forEach((a) => {
        const href = a.getAttribute("href") || "";
        const target = href.split("/").pop();
        if (target && target === here) a.classList.add("active");
      });
  }

  /* ---------------- Broken-link detector (report only) ----------------
     Checks every internal link on load. Reports broken ones to the
     console and a toast. It NEVER rewrites or removes any href.        */
  function initBrokenLinkDetector(): void {
    const links = Array.from(
      document.querySelectorAll<HTMLAnchorElement>("a[href]"),
    );
    const internal = links.filter((a) => {
      const h = a.getAttribute("href") || "";
      return h && !/^(https?:|mailto:|tel:|#|javascript:|data:)/i.test(h);
    });
    if (!internal.length) return;

    // Only run when explicitly enabled or on a local host (perf-friendly).
    const enabled =
      new URLSearchParams(location.search).has("checkLinks") ||
      location.hostname === "localhost" ||
      location.hostname === "127.0.0.1";
    if (!enabled) return;

    let pending = internal.length;
    const broken: HTMLAnchorElement[] = [];
    internal.forEach((a) => {
      const url = new URL(a.getAttribute("href") as string, location.href);
      fetch(url.href, { method: "HEAD", mode: "no-cors" })
        .then((r) => {
          // no-cors opaque responses can't reveal status; only flag
          // same-origin failures precisely.
          if (url.origin === location.origin && r.type === "error") {
            broken.push(a);
          }
        })
        .catch(() => {
          if (url.origin === location.origin) broken.push(a);
        })
        .finally(() => {
          pending -= 1;
          if (pending === 0 && broken.length) reportBroken(broken);
        });
    });

    function reportBroken(list: HTMLAnchorElement[]): void {
      console.warn(
        "[MY BOOKSHELF] Broken internal links detected (reported only, not modified):",
        list.map((a) => a.getAttribute("href")),
      );
      showToast(
        "⚠ តំណភ្ជាប់ខូចមួយចំនួនត្រូវបានរកឃើញ (សូមមើល console)",
        5000,
      );
    }
  }

  /* ---------------- Boot ----------------
     Download-card behaviour stays in each page's own script (page-specific
     and already null-guarded). The shared script handles navigation, theme,
     footer reveal, active links, and link checks. */
  function boot(): void {
    initFooterReveal();
    initNav();
    initTheme();
    initActiveNav();
    initBrokenLinkDetector();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
