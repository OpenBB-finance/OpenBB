import Link from "@docusaurus/Link";
import React from "react";
import clsx from "clsx";

import { useLocation } from "@docusaurus/router";

export default function ReferenceCard({
  title,
  url,
  description,
  command,
}: {
  title: string;
  url: string;
  description: string;
  command: string;
}) {
  // TODO: Waiting for mockup of how to display the command vs menu item
  const something = command ? "" : "";
  const { pathname } = useLocation();
  return (
    <Link
      className={clsx(
        "rounded border-2 !no-underline border-grey-600 p-6 cursor-pointer relative overflow-hidden hover:shadow-2xl hover:-translate-y-2 transform transition-all duration-300 ease-in-out font-bold shadow-2xl",
        {header_docs_terminal: pathname.startsWith("/terminal"),
        "bg-gradient-to-r from-[#541c12] to-[rgba(84, 29, 19, 1)]" : pathname.startsWith("/sdk"),
        "bg-gradient-to-r from-grey-800 to-purple-800" : pathname.startsWith("/bot"),
        header_docs:
          !pathname.startsWith("/terminal") &&
          !pathname.startsWith("/sdk") &&
          !pathname.startsWith("/bot"),
      }
        )}
      to={url}
    >
      <div className="absolute top-0 right-0 left-0 bottom-0 bg-gradient-to-t from-black to-transparent"></div>
      <p className={"py-2 font-bold text-lg my-0"}>{title}{something}</p>
      {description ? (
        <p className="text-grey-200 text-xs mt-2 mb-0">{description}</p>
      ) : null}
    </Link>
  );
}
