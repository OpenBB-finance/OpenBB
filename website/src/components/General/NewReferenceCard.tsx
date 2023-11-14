import Link from "@docusaurus/Link";
import clsx from "clsx";
import React from "react";

import { useLocation } from "@docusaurus/router";
import ChevronRightIcon from "../Icons/ChevronRight";

export default function NewReferenceCard({
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
  const cleanedPath = pathname.replace(/\/v\d+/, "");
  return (
    <Link
      className={clsx(
        "rounded border-2 hover:!text-black dark:hover:!text-white !no-underline p-6 cursor-pointer relative overflow-hidden hover:shadow-2xl hover:-translate-y-2 transform transition-all duration-300 ease-in-out font-bold shadow-2xl",
        {
          "bg-[#669DCB] dark:bg-[#004A87]": cleanedPath.startsWith("/terminal"),
          "bg-[#F5B166] dark:bg-[#511d11]": cleanedPath.startsWith("/sdk") || cleanedPath.startsWith("/platform"),
          "bg-[#b186bb] border-[#b186bb] hover:border-black dark:bg-[#3a204f] dark:border-[#3a204f] dark:hover:border-white": cleanedPath.startsWith("/bot"),
          header_docs:
            !cleanedPath.startsWith("/terminal") &&
            !cleanedPath.startsWith("/sdk") &&
            !cleanedPath.startsWith("/platform") &&
            !cleanedPath.startsWith("/bot"),
        },
      )}
      to={url}
    >
      <div className="absolute top-0 right-0 left-0 bottom-0" />
      <p className={"py-2 font-bold text-lg my-0"}>
        {title}
        {something}
      </p>
      <ChevronRightIcon className="absolute top-0 right-0 bottom-0 my-auto mr-4" />
      {description ? (
        <p className="text-grey-900 dark:text-grey-200 text-xs font-medium mt-2 mb-0">{description}</p>
      ) : null}
    </Link>
  );
}
