import React from "react";
import LetteringLogo from "@site/src/components/Icons/LetteringLogo";
import { useLocation } from "@docusaurus/router";
import Link from "@docusaurus/Link";
import TerminalLetteringLogo from "@site/src/components/Icons/TerminalLetteringLogo";
import SDKLetteringLogo from "@site/src/components/Icons/SDKLetteringLogo";
import BotLetteringLogo from "@site/src/components/Icons/BotLetteringLogo";

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
  return (
    <div className="flex items-center gap-x-[56px]">
      <Link to="/" className="mb-1 md:mb-0 md:ml-0">
        {getLogo(type)}
      </Link>
    </div>
  );
}
