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
  const chevron =
    !cleanedPath.includes("/reference") &&
    !cleanedPath.includes("/widgets-library/") &&
    !cleanedPath.includes("/data_models");

  return (
    <Link
      className={clsx(
        "rounded border-2 hover:!text-black dark:hover:!text-white !no-underline p-6 cursor-pointer relative overflow-hidden hover:-translate-y-2 transform transition-all duration-300 ease-in-out font-bold shadow-md",
        {
          "hover:bg-[#669DCB] border-[#669DCB] dark:hover:bg-[#004A87] dark:border-[#004A87]":
            cleanedPath.startsWith("/terminal") ||
            cleanedPath.startsWith("/pro") ||
            cleanedPath.startsWith("/excel"),
          "hover:bg-[#b186bb] border-[#b186bb] dark:hover:bg-[#3a204f] dark:border-[#3a204f]":
            cleanedPath.startsWith("/bot"),
          "hover:bg-[#F5B166] border-[#F5B166] dark:hover:bg-[#511d11] dark:border-[#511d11]":
            cleanedPath.startsWith("/sdk") ||
            cleanedPath.startsWith("/platform"),
          header_docs:
            !cleanedPath.startsWith("/terminal") &&
            !cleanedPath.startsWith("/pro") &&
            !cleanedPath.startsWith("/excel") &&
            !cleanedPath.startsWith("/sdk") &&
            !cleanedPath.startsWith("/platform") &&
            !cleanedPath.startsWith("/bot"),
        },
      )}
      to={url}
    >
      <div className="absolute top-0 right-0 left-0 bottom-0" />
      <div className="flex items-center">
        <p className={"py-2 font-bold text-lg my-0"}>
          {title}
          {something}
        </p>
        {chevron && <ChevronRightIcon className="ml-auto mr-4" />}
      </div>
      {description ? (
        <p className="text-grey-900 dark:text-grey-200 text-xs font-medium mt-2 mb-0">
          {description}
        </p>
      ) : null}
    </Link>
  );
}
