import React from "react";
import Terminal from "../Terminal";

interface Props {
  title: string;
  description: string;
  url: string;
  children: any;
  categories: string[];
}

export default function ShowcaseItem({
  title,
  description,
  url,
  children,
  categories,
}: Props) {
  return (
    <div>
      <div className="flex gap-3 items-center">
        <h3 className="font-bold text-xl my-4">{title}</h3>
        <div className="flex gap-2 items-center">
          {categories.map((category) => (
            <span className="bg-grey-50 h-[22px] rounded dark:bg-grey-800 dark:text-white px-3 py-0.5 text-xs">
              {category}
            </span>
          ))}
        </div>
      </div>
      <p className="dark:text-grey-100">{description}</p>
      <a href={url} className="text-sm">
        {url}
      </a>
      <Terminal rootClassnames="mt-10">{children}</Terminal>
    </div>
  );
}
