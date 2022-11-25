import React, { useEffect } from "react";
import clsx from "clsx";
import { useThemeConfig } from "@docusaurus/theme-common";
import {
  useHideableNavbar,
  useNavbarMobileSidebar,
} from "@docusaurus/theme-common/internal";
import NavbarMobileSidebar from "@theme/Navbar/MobileSidebar";
import styles from "./styles.module.css";
import { useLocation } from "@docusaurus/router";
function NavbarBackdrop(props) {
  return (
    <div
      role="presentation"
      {...props}
      className={clsx("navbar-sidebar__backdrop", props.className)}
    />
  );
}
export default function NavbarLayout({ children }) {
  const {
    navbar: { hideOnScroll, style },
  } = useThemeConfig();
  const { pathname } = useLocation();
  const mobileSidebar = useNavbarMobileSidebar();
  const { navbarRef, isNavbarVisible } = useHideableNavbar(hideOnScroll);

  useEffect(() => {
    if (pathname.startsWith("/terminal")) {
      document.documentElement.style.setProperty(
        "--ifm-color-primary",
        "#669DCB"
      );
    } else if (pathname.startsWith("/sdk")) {
      document.documentElement.style.setProperty(
        "--ifm-color-primary",
        "#F5B166"
      );
    } else {
    }
  }, [pathname]);
  return (
    <nav
      ref={navbarRef}
      className={clsx(
        "border-b border-grey-600 lg:px-12",
        {
          header_docs_terminal: pathname.startsWith("/terminal"),
          header_docs_sdk: pathname.startsWith("/sdk"),
          header_docs: !pathname.startsWith("/terminal") && !pathname.startsWith("/sdk"),
        },
        "navbar",
        "navbar--fixed-top",
        hideOnScroll && [
          styles.navbarHideable,
          !isNavbarVisible && styles.navbarHidden,
        ],
        {
          "navbar--dark": style === "dark",
          "navbar--primary": style === "primary",
          "navbar-sidebar--show": mobileSidebar.shown,
        }
      )}
    >
      {children}
      <NavbarBackdrop onClick={mobileSidebar.toggle} />
      <NavbarMobileSidebar />
    </nav>
  );
}
