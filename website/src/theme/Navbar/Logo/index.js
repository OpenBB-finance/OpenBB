import Link from "@docusaurus/Link";
import { useLocation } from "@docusaurus/router";
import LetteringLogo from "@site/src/components/Icons/LetteringLogo";
import React from "react";

function getLogo(type) {
  /*
  switch (type) {
    case "terminal":
      return <TerminalLetteringLogo />;
    case "sdk":
      return <SDKLetteringLogo />;
    case "bot":
      return <BotLetteringLogo />;
    default:
      return <LetteringLogo className="text-white" />;
  }*/
  return <LetteringLogo className="text-white" />;
}

export default function NavbarLogo() {
  const { pathname } = useLocation();
  const type = pathname.length > 1 ? pathname.split("/")[1] : "home";
  const version = pathname.length > 1 ? pathname.split("/")[1] : "home";
  return (
    <div className="flex items-center gap-x-[56px]">
      <Link to={version.charAt(0) === "v" ? `/${version}` : ""} className="mb-1 md:mb-0 md:ml-0">
        {getLogo(type)}
      </Link>
    </div>
  );
}
