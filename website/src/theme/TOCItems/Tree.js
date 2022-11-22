import clsx from "clsx";
import React from "react";
// Recursive component rendering the toc tree
function TOCItemTree({ toc, className, linkClassName, isChild }) {
  if (!toc.length) {
    return null;
  }
  return (
    <ul
      className={
        isChild ? "list-none ml-1 border-l border-grey-300 dark:border-grey-600 mt-2" : "border-l border-grey-300 dark:border-grey-600 list-none pl-4" /*className*/
      }
    >
      {toc.map((heading, idx) => (
        <li key={heading.id} className={clsx({
          "pb-1": idx === 0,
          "py-1": idx !== 0,
          "pl-3": isChild
        })}>
          {/* eslint-disable-next-line jsx-a11y/control-has-associated-label */}
          <a
            href={`#${heading.id}`}
            className={linkClassName ?? undefined}
            // Developer provided the HTML, so assume it's safe.
            // eslint-disable-next-line react/no-danger
            dangerouslySetInnerHTML={{ __html: heading.value }}
          />
          <TOCItemTree
            isChild
            toc={heading.children}
            className={className}
            linkClassName={linkClassName}
          />
        </li>
      ))}
    </ul>
  );
}
// Memo only the tree root is enough
export default React.memo(TOCItemTree);
