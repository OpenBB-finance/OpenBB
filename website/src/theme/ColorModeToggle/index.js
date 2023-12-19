import React, { useEffect } from "react";
import clsx from "clsx";
import useIsBrowser from "@docusaurus/useIsBrowser";
import { translate } from "@docusaurus/Translate";
import * as PopoverPrimitive from "@radix-ui/react-popover";
import SunIcon from "@site/src/components/Icons/Sun";
import MoonIcon from "@site/src/components/Icons/Moon";
import { useLocation } from "@docusaurus/router";
import DiscordIcon from "@site/src/components/Icons/Discord";
import TelegramIcon from "@site/src/components/Icons/Telegram";
import Link from "@docusaurus/Link";
import { useIFrameContext } from "../Root";
function ColorModeToggle({ className, value, onChange }) {
  const { isIFrame } = useIFrameContext();
  const { pathname } = useLocation();
  const showBotChange = false; //pathname.startsWith("/bot/discord") || pathname.startsWith("/bot/telegram");
  // this can be used later to switch between discord and telegram commands on bot
  const isDiscord = pathname.startsWith("/bot/discord");
  const isBrowser = useIsBrowser();
  const title = translate(
    {
      message: "Switch between dark and light mode (currently {mode})",
      id: "theme.colorToggle.ariaLabel",
      description: "The ARIA label for the navbar color mode toggle",
    },
    {
      mode:
        value === "dark"
          ? translate({
              message: "dark mode",
              id: "theme.colorToggle.ariaLabel.mode.dark",
              description: "The name for the dark color mode",
            })
          : translate({
              message: "light mode",
              id: "theme.colorToggle.ariaLabel.mode.light",
              description: "The name for the light color mode",
            }),
    }
  );
  const command = pathname.split("/").pop();
  useEffect(() => {
    if (isIFrame) {
      onChange("dark");
    }
  }, []);
  return (
    <div className="flex gap-4 mr-12 md:mr-0 ml-4">
      {showBotChange && (
        <PopoverPrimitive.Root>
          <PopoverPrimitive.Trigger className="bg-grey-900 radix-state-open:text-white hover:border-grey-200 hover:text-grey-200 radix-state-open:border-white border -mt-[0.6px] h-[34px] w-[34px] text-grey-400 border-grey-400 rounded flex items-center justify-center">
            {isDiscord ? (
              <DiscordIcon className="w-4 h-4" />
            ) : (
              <TelegramIcon className="w-4 h-4" />
            )}
          </PopoverPrimitive.Trigger>
          <PopoverPrimitive.Content
            sideOffset={5}
            align="start"
            className={clsx(
              "z-50 bg-grey-900 border text-white border-grey-200 rounded flex flex-col divide-y divide-grey-600 p-4"
            )}
          >
            <Link
              className={clsx("text-sm inline-flex pb-3 hover:text-white", {
                "text-grey-400": !isDiscord,
                "text-white": isDiscord,
              })}
              type="button"
              href={`/bot/discord/${command}`}
              disabled={!isBrowser}
              title={title}
              aria-label={title}
              aria-live="polite"
            >
              <DiscordIcon className="w-4 h-4 mr-2 mt-0.5" /> Discord
            </Link>
            <Link
              className={clsx("text-sm inline-flex pt-3 hover:text-white", {
                "text-grey-400": isDiscord,
                "text-white": !isDiscord,
              })}
              type="button"
              href={`/bot/telegram/${command}`}
              disabled={!isBrowser}
              title={title}
              aria-label={title}
              aria-live="polite"
            >
              <TelegramIcon className="w-4 h-4 mr-2 mt-0.5" /> Telegram
            </Link>
          </PopoverPrimitive.Content>
        </PopoverPrimitive.Root>
      )}
      <PopoverPrimitive.Root>
        <PopoverPrimitive.Trigger className="bg-grey-900 radix-state-open:text-white hover:border-grey-200 hover:text-grey-200 radix-state-open:border-white border -mt-[0.6px] h-[34px] w-[34px] text-grey-400 border-grey-400 rounded flex items-center justify-center">
          {value !== "dark" ? (
            <SunIcon className="w-4 h-4" />
          ) : (
            <MoonIcon className="w-4 h-4" />
          )}
        </PopoverPrimitive.Trigger>
        <PopoverPrimitive.Content
          sideOffset={5}
          align="start"
          className={clsx(
            "z-50 bg-grey-900 border text-white border-grey-200 rounded flex flex-col divide-y divide-grey-600 p-4"
          )}
        >
          <button
            className={clsx("text-sm inline-flex pb-3 hover:text-white", {
              "text-grey-400": value === "dark",
              "text-white": value !== "dark",
            })}
            type="button"
            onClick={() => {
              onChange("light")
              window.location.reload();
            }}
            disabled={!isBrowser}
            title={title}
            aria-label={title}
            aria-live="polite"
          >
            <SunIcon className="w-4 h-4 mr-2 mt-0.5" /> Light
          </button>
          <button
            className={clsx("text-sm inline-flex pt-3 hover:text-white", {
              "text-grey-400": value !== "dark",
              "text-white": value === "dark",
            })}
            type="button"
            onClick={() => {
              onChange("dark")
              window.location.reload();
            }}
            disabled={!isBrowser}
            title={title}
            aria-label={title}
            aria-live="polite"
          >
            <MoonIcon className="w-4 h-4 mr-2 mt-0.5" /> Dark
          </button>
        </PopoverPrimitive.Content>
      </PopoverPrimitive.Root>
      {/*<button className="relative flex items-center justify-center md:justify-start bg-grey-900 p-2 border text-grey-400 border-grey-400 hover:text-grey-200 active:text-white focus:outline-grey-500 focus:outline hover:border-grey-200 rounded md:w-[200px] input gap-3">
        <span className='text-xs whitespace-nowrap'>Search...</span>
        <span className="absolute right-1.5 px-1.5 text-grey-400 border border-grey-400/50 rounded text-[10px] items-center gap-1 hidden sm:flex">CTRL+K</span>
        </button>*/}
    </div>
  );
}
export default React.memo(ColorModeToggle);
