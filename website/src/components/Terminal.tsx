import React from "react";
import type { ReactElement } from "react";
import clsx from "clsx";

export default function Terminal({
  extraClassnames = "",
  rootClassnames = "",
  children,
}: {
  children: JSX.Element | JSX.Element[];
  extraClassnames?: string;
  rootClassnames?: string;
}) {
  return (
    <div className={rootClassnames}>
      <div className="flex h-6 w-full items-center justify-between rounded-t-lg border-b bg-grey-100 dark:bg-white px-4 md:h-8">
        <div className="flex h-full items-center gap-x-2">
          <div className="h-2 w-2 rounded-full bg-grey-400 md:h-3 md:w-3" />
          <div className="h-2 w-2 rounded-full bg-grey-400 md:h-3 md:w-3" />
          <div className="h-2 w-2 rounded-full bg-grey-400 md:h-3 md:w-3" />
        </div>
      </div>
      <div
        className={clsx(
          "rounded-b-lg border-b-2  border-l-2 border-r-2 border-grey-100 dark:border-white bg-black dark:text-white",
          extraClassnames
        )}
      >
        {children}
      </div>
    </div>
  );
}
