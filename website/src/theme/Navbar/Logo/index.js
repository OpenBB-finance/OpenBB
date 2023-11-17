import Link from "@docusaurus/Link";
import { useLocation } from "@docusaurus/router";
import LetteringDocsLogo from "@site/src/components/Icons/LetteringDocsLogo";
import React from "react";

function getLogo(type) {
  return <LetteringDocsLogo />;
}

export default function NavbarLogo() {
  const { pathname } = useLocation();
  const type = pathname.length > 1 ? pathname.split("/")[1] : "home";

  return (
    <div className="flex items-center ml-2" style={{ display: window.innerWidth < 380 ? 'none' : 'flex' }}>
      <Link to={`/${type}`}>
        {getLogo(type)}
      </Link>
    </div>
  );
}
