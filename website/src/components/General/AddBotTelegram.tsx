import TelegramIcon from "../Icons/Telegram";
import React from "react";

export default function AddBotDialogTelegram() {
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
        </div>
  );
}
