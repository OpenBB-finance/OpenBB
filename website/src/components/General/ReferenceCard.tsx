import Link from "@docusaurus/Link";
import React from "react";

export default function ReferenceCard({
  title,
  url,
  description,
}: {
  title: string;
  url: string;
  description: string;
}) {
  return (
    <Link
      className="rounded border !no-underline border-grey-400 bg-black p-6 cursor-pointer relative overflow-hidden"
      to={url}
    >
      <p className="font-bold text-lg my-0">{title}</p>
      {description ? (
        <p className="text-grey-200 text-xs mt-2 mb-0">{description}</p>
      ) : null}
    </Link>
  );
}
