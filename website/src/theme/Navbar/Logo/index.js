import Link from "@docusaurus/Link";
import { useLocation } from "@docusaurus/router";
import LetteringDocsLogo from "@site/src/components/Icons/LetteringDocsLogo";
import clsx from "clsx";
import React from "react";

function getLogo(type) {
  return <LetteringDocsLogo />;
}

export default function NavbarLogo() {
  const { pathname } = useLocation();
  const type = pathname.length > 1 ? pathname.split("/")[1] : "home";
  const [innerWidth, setInnerWidth] = React.useState(380);

  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener("resize", () => {
        setInnerWidth(window.innerWidth);

      });
    }
  }
  , []);


  return (
    <div className={clsx("items-center ml-2", innerWidth < 380 ? "hidden" : "flex")}>
      <Link to={`/`}>
        {getLogo(type)}
      </Link>
    </div>
  );
}
