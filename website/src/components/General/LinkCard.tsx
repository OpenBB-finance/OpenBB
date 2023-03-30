import clsx from "clsx";
import React from "react";
import ChevronRightIcon from "../Icons/ChevronRight";
import Link from "@docusaurus/Link";
import WindowsIcon from "../Icons/Windows";
import DockerIcon from "../Icons/Docker";
import AppleIcon from "../Icons/Apple";
import SourceIcon from "../Icons/Source";
import DiscordIcon from "../Icons/Discord";
import TelegramIcon from "../Icons/Telegram";
import PipIcon from "../Icons/PipIcon";

interface CardProps {
  title: string;
  description: string;
  className?: string;
  type?: "terminal" | "sdk" | "bot";
  url: string;
  platform?: "windows" | "macos" | "source" | "docker" | "discord" | "telegram" | "pypi";
}

export default function Card({
  title,
  description,
  className = "mb-8",
  type = "terminal",
  platform,
  url = "/"
}: CardProps) {
  return (
    <Link
    className="flex !no-underline h-full p-2 items-center justify-between cursor-pointer relative w-2/4 rounded-t-lg"
    //    className="flex !no-underline p-6 items-center cursor-pointer relative w-2/4 rounded-t-lg"
    to={url}
  >
    <div
      style={{
        backgroundImage:
          type === "terminal"
            ? "url('/img/terminal_bg.png')"
            : type === "sdk"
            ? "url('/img/sdk_bg.png')"
            : "url('/img/bot_bg.png')",
        backgroundRepeat: "no-repeat",
        backgroundSize: "100% 130%",
      }}
      // <div className="flex h-6 w-full items-center justify-between rounded-t-lg border-b bg-grey-100 dark:bg-white px-4 md:h-8">
      // <div className="flex h-full items-center gap-x-2">
      className={clsx(
        "shadow-sm group !no-underline text-grey-900 dark:text-white hover:text-grey-900 dark:hover:border-white hover:border-grey-900 dark:hover:!text-white relative w-full max-w-full p-5 rounded-lg border border-grey-400 bg-white dark:bg-grey-900",
        className
      )}
    >
      <p className="uppercase tracking-widest font-bold text-lg inline-flex gap-4 h-2 items-center">
        {platform === "windows" && (
          <WindowsIcon className="w-4 h-4" />
        )}
        {platform === "macos" && (
          <AppleIcon className="w-4 h-4" />
        )}
        {platform === "source" && (
          <SourceIcon className="w-4 h-4" />
        )}
        {platform === "pypi" && (
          <PipIcon className="w-4 h-4" />
        )}
        {platform === "docker" && (
          <DockerIcon className="w-4 h-4" />
        )}
        {platform === "discord" && (
          <DiscordIcon className="w-4 h-4" />
        )}
        {platform === "telegram" && (
          <TelegramIcon className="w-4 h-4" />
        )}
        {title}
        </p>
      <p className="text-sm dark:text-grey-300">{description}</p>
      {false && (
        <p
          className={clsx("mt-auto inline-flex items-center gap-2 font-normal")}
        >
          See more
          <ChevronRightIcon className="group-hover:translate-x-2 tw-transition w-3" />
        </p>
      )}
    </div>
  </Link>
  );
}
