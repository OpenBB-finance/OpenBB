import Link from "@docusaurus/Link";
import React from "react";

export default function TemplateCard({
  title,
  description,
  imageUrl,
  downloadUrl,
}: {
  title: string;
  description: string;
  imageUrl: string;
  downloadUrl: string;
}) {
  return (
    <Link className="rounded-lg p-5 !bg-grey-100 dark:!bg-black !text-white !no-underline relative overflow-hidden">
      <div className="flex min-h-[180px]">
        <div style={{ width: "40%" }}>
          <img className="w-full h-auto mb-0 mt-0" src={imageUrl} alt={title} />
        </div>
        <div className="flex flex-col ml-5" style={{ width: "60%" }}>
          <p className="font-bold text-lg my-0 text-grey-900 dark:text-grey-200">
            {title}
          </p>
          <p className="text-grey-900 dark:text-grey-200 text-xs font-medium mt-2 mb-0 leading-5">
            {description}
          </p>
          <div className="flex-grow flex items-end justify-start mt-5">
            <button
              onClick={() => (window.location.href = downloadUrl)}
              className="bg-white dark:bg-[#303038] text-grey-900 dark:text-grey-200 text-sm font-medium py-2 px-4 rounded"
            >
              Download
            </button>
          </div>
        </div>
      </div>
    </Link>
  );
}
