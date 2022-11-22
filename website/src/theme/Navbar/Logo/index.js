import React from "react";
import LetteringLogo from "@site/src/components/Icons/LetteringLogo";
import clsx from "clsx";
import { useLocation } from "@docusaurus/router";
import Link from "@docusaurus/Link";

export default function NavbarLogo() {
  const { pathname } = useLocation();
  return (
    <div className="flex items-center gap-x-[56px]">
      <Link to="/" className="ml-5 mb-1 md:mb-0 md:ml-0">
        <LetteringLogo className="text-white" />
      </Link>
      <div
        className={clsx(
          "hidden p-2 border border-grey-400 rounded h-[34px] items-center bg-grey-900 gap-3",
          {
            "md:flex": pathname !== "/",
          }
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
    </div>
  );
}
