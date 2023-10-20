import Link from "@docusaurus/Link";
import { useLocation } from "@docusaurus/router";
import LetteringLogo from "@site/src/components/Icons/LetteringLogo";
import OnlyBotLetteringLogo from "@site/src/components/Icons/OnlyBotLettering";
import OnlyProLetteringLogo from "@site/src/components/Icons/OnlyProLettering";
import OnlySDKLetteringLogo from "@site/src/components/Icons/OnlySDKLettering";
import OnlyPlatformLettering from "@site/src/components/Icons/OnlyPlatformLettering";
import OnlyTerminalLetteringLogo from "@site/src/components/Icons/OnlyTerminalLettering";
import React from "react";
import OnlyPlatformLetteringLogo from "@site/src/components/Icons/OnlyPlatformLettering";

function getLogo(type) {
  switch (type) {
    case "hub":
      return <LetteringLogo />;
    case "terminal":
      return (
        <div className="flex mb-0">
          <LetteringLogo />
          <div className="pt-2 mx-4">
            <OnlyTerminalLetteringLogo />
          </div>
        </div>
      );
    case "platform":
      return (
        <div className="flex mb-0">
          <LetteringLogo />
          <div className="pt-2 mx-4">
            <OnlyPlatformLetteringLogo />
          </div>
        </div>
      );
    case "sdk":
      return (
        <div className="flex mb-0">
          <LetteringLogo />
          <div className="pt-2 mx-4">
            <OnlySDKLetteringLogo />
          </div>
        </div>
      );
    case "pro":
      return (
        <div className="flex mb-0">
          <LetteringLogo />
          <div className="pt-2 mx-4">
            <OnlyProLetteringLogo />
          </div>
        </div>
      );
    case "bot":
      return (
        <div className="flex mb-0">
          <LetteringLogo />
          <div className="pt-2 mx-4">
            <OnlyBotLetteringLogo />
          </div>
        </div>
      );
  }
}

export default function NavbarLogo() {
  const { pathname } = useLocation();
  const type = pathname.length > 1 ? pathname.split("/")[1] : "home";
  return (
    <div className="flex items-center gap-x-[56px]">
      <Link to="/" className="mb-1 md:mb-0 md:ml-0">
        {getLogo(type)}
      </Link>
      {type === "sdk" && (
        <div className="text-white text-xs pt-2">
          OpenBB SDK has been deprecated in detriment of the Platform. More details here.
        </div>
      )}
    </div>
  );
}
