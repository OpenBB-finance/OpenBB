import React, { useEffect, useState } from "react";
import { ThemeClassNames } from "@docusaurus/theme-common";
import { useDoc } from "@docusaurus/theme-common/internal";
import TOC from "@theme/TOC";
export default function DocItemTOCDesktop() {
  const { toc, frontMatter } = useDoc();

  /*const [currentToc, setCurrentToc] = useState(toc);
  useEffect(() => {
    const modelElements = document.getElementsByClassName("tabs__item");
    let observer = null;
    if (modelElements && modelElements.length == 2) {
      const modelElement = modelElements[0];
      const modelSelected = modelElement.ariaSelected;
      if (modelSelected === "true") {
        setCurrentToc(toc.slice(0, 4));
      } else {
        setCurrentToc(toc.slice(4, 8));
      }

      observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
          console.log(mutation);
          if (mutation.type === "attributes") {
            const modelSelected = mutation.target.ariaSelected;
            if (modelSelected === "true") {
              setCurrentToc(toc.slice(0, 4));
            } else {
              setCurrentToc(toc.slice(4, 8));
            }
          }
        });
      });
      observer.observe(modelElement, {
        attributes: true,
      });
    }
    return () => observer?.disconnect();
  }, []);*/
  return (
    <TOC
      toc={toc}
      minHeadingLevel={frontMatter.toc_min_heading_level}
      maxHeadingLevel={frontMatter.toc_max_heading_level}
      className={ThemeClassNames.docs.docTocDesktop}
    />
  );
}
