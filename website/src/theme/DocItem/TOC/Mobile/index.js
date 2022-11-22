import React from 'react';
import clsx from 'clsx';
import { ThemeClassNames } from '@docusaurus/theme-common';
import { useDoc } from '@docusaurus/theme-common/internal';
import TOCCollapsible from '@theme/TOCCollapsible';
import styles from './styles.module.css';
import { useLocation } from '@docusaurus/router';
export default function DocItemTOCMobile() {
  const { toc, frontMatter } = useDoc();
  const { pathname } = useLocation()
  if (pathname.startsWith("/sdk/reference/")) return null
  return (
    <TOCCollapsible
      toc={toc}
      minHeadingLevel={frontMatter.toc_min_heading_level}
      maxHeadingLevel={frontMatter.toc_max_heading_level}
      className={clsx(ThemeClassNames.docs.docTocMobile, styles.tocMobile)}
    />
  );
}
