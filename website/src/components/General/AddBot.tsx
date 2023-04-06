import DiscordIcon from "../Icons/Discord";
import TelegramIcon from "../Icons/Telegram";
import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import InfoIcon from "../Icons/Info";
import React, { useState } from "react";

export default function AddBotDialog() {
  return (
        <div className="mt-10 flex flex-col justify-center items-center gap-6">
          <a
            href="https://openbb.co/bot-telegram"
            target="_blank"
            className="_btn h-[38px] gap-3 text-xs !bg-[#20A0E1] !hover:bg-[#1D90CB] active:bg-[#1A80B4] text-white hover:text-white"
            rel="noopener noreferrer"
          >
            <TelegramIcon /> Add bot to Telegram
          </a>
          <div className="relative w-full md:w-auto">
            <a
              href="https://openbb.co/bot-discord"
              className="_btn relative md:w-[217px] h-[38px] gap-3 text-xs !bg-[#5865F2] !hover:bg-[#4651C2] active:bg-[#353D91] text-white hover:text-white"
              target="_blank"
              rel="noopener noreferrer"
            >
              <DiscordIcon /> Add bot to Discord
            </a>
            <Tooltip />
          </div>
        </div>
  );
}

function Tooltip() {
  const [open, setOpen] = useState(false);
  return (
    <TooltipPrimitive.Provider delayDuration={100}>
      <TooltipPrimitive.Root open={open}>
        <TooltipPrimitive.Trigger
          onClick={() => {
            if (!open) {
              setOpen(true);
            }
          }}
          onMouseOver={() => setOpen(true)}
          onMouseLeave={() => setOpen(false)}
          className="absolute -right-6 top-0"
        >
          <InfoIcon className="w-[18px] h-[18px] text-grey-300" />
        </TooltipPrimitive.Trigger>
        <TooltipPrimitive.Content
          sideOffset={5}
          side="top"
          className="text-[10px] px-2 py-1 bg-grey-900 border border-grey-300 rounded-[4px] slide-up-fade w-[180px]"
        >
          You must be a server owner
        </TooltipPrimitive.Content>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  );
}
