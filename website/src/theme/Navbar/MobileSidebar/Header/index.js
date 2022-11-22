import React from 'react';
import { useNavbarMobileSidebar } from '@docusaurus/theme-common/internal';
import { translate } from '@docusaurus/Translate';
import NavbarColorModeToggle from '@theme/Navbar/ColorModeToggle';
import IconClose from '@theme/Icon/Close';
import NavbarLogo from '@theme/Navbar/Logo';
import Link from '@docusaurus/Link';
import clsx from 'clsx';
import { useLocation } from '@docusaurus/router';
function CloseButton() {
  const mobileSidebar = useNavbarMobileSidebar();
  return (
    <button
      type="button"
      aria-label={translate({
        id: 'theme.docs.sidebar.closeSidebarButtonAriaLabel',
        message: 'Close navigation bar',
        description: 'The ARIA label for close button of mobile sidebar',
      })}
      className="clean-btn navbar-sidebar__close"
      onClick={() => mobileSidebar.toggle()}>
      <IconClose color="var(--ifm-color-emphasis-600)" />
    </button>
  );
}
export default function NavbarMobileSidebarHeader() {
  const { pathname } = useLocation();

  return (
    <div className="navbar-sidebar__brand">
      <div
        className={clsx(
          "flex p-2 border border-grey-400 rounded h-[34px] items-center bg-grey-900 gap-3",
        )}
      >
        <Link
          to="/terminal"
          className={clsx(
            "text-xs rounded px-2 py-1 hover:text-white hover:no-underline",
            {
              "text-grey-100 bg-grey-800 ":
                pathname.startsWith("/terminal"),
              "text-grey-500 hover:bg-grey-800 ":
                !pathname.startsWith("/terminal"),
            }
          )}
        >
          Terminal
        </Link>
        <Link
          to="/sdk"
          className={clsx(
            "text-xs px-2 py-1 rounded hover:text-white hover:no-underline",
            {
              "text-grey-100 bg-grey-800 ": pathname.startsWith("/sdk"),
              "text-grey-500 hover:bg-grey-800 ":
                !pathname.startsWith("/sdk"),
            }
          )}
        >
          SDK
        </Link>
      </div>
      <NavbarColorModeToggle />
      <CloseButton />
    </div>
  );
}
