import Link from "@docusaurus/Link";
import Layout from "@theme/Layout";
import clsx from "clsx";
import React from "react";
import ChevronRightIcon from "../components/Icons/ChevronRight";
import DarkBlueRadialGradient from "../components/Icons/RadialGradients/DarkBlue";
import RubyRedRadialGradient from "../components/Icons/RadialGradients/RubyRed";
import CloseIcon from "../components/Icons/Close"

export default function Home(): JSX.Element {
  return (
    <Layout description="Documentation for free and open source OpenBB products.">
      <article className="min-h-[75vh] w-full relative py-20 md:py-10 flex flex-col items-center justify-center overflow-hidden">
        <DarkBlueRadialGradient className="absolute opacity-40 -left-[1000px] w-[1600px] h-[1600px] lg:-left-[1000px] lg:opacity-40 -top-20 xl:-top-60 xl:-left-[800px] 2xl:opacity-50" />
        <RubyRedRadialGradient className="absolute opacity-40 -right-[1000px] w-[1600px] h-[1600px] lg:-right-[1000px] lg:opacity-40 -top-20 xl:-top-60 xl:-right-[800px] 2xl:opacity-50" />
        <div className="flex mx-auto flex-col items-center justify-center w-full max-w-[1100px]">
          <div className="z-10 flex flex-col items-center justify-center w-full h-full mb-10 md:mb-0">
            <h1 className="mx-6 font-bold text-2xl lg:text-3xl xl:text-4xl leading-10 text-center mb-4 tracking-widest uppercase">
              OpenBB Documentation
            </h1>
            <p className="mx-6 w-[315px] md:w-[880px] text-sm lg:text-lg xl:text-xl text-center text-grey-900 dark:text-white">
              All the documentation for the tools you need for your investment research.
            </p>
          </div>
          <div className="flex flex-col md:flex-row w-full container items-center justify-center gap-6 px-6 sm:mx-0">
            <Link
              style={{
                backgroundSize: "100% 130%",
              }}
              to="/pro"
              className="!bg-grey-900 bg-[url('/img/pro.png')] bg-no-repeat shadow-sm group !no-underline text-white dark:hover:border-white hover:border-grey-600/80 relative w-full h-[238px] max-w-full p-8 rounded flex flex-col items-start justify-start border border-grey-300 hover:!text-white"
            >
              <h3 className="uppercase tracking-widest font-bold mb-0 mt-0 text-white">
                OpenBB Terminal Pro [EARLY ACCESS]
              </h3>
              <p className="text-sm lg:text-base dark:text-grey-300">
                The OpenBB Terminal Pro is the investment research platform for the 21st century.
              </p>
              <p
                className={clsx(
                  "mt-auto inline-flex items-center gap-1 font-normal text-sm",
                )}
              >
                See more
                <ChevronRightIcon className="group-hover:translate-x-2 tw-transition w-3" />
              </p>
            </Link>
          </div>
          <div className="flex flex-col md:flex-row w-full container items-center justify-center gap-6 px-6 sm:mx-0 my-8 lg:!my-10">
            <Link
              style={{
                backgroundSize: "100% 130%",
              }}
              to="/platform"
              className="!bg-grey-900 bg-[url('/img/sdk_bg.png')] bg-no-repeat shadow-sm group !no-underline text-white dark:hover:border-white hover:border-grey-600/80 relative w-full h-[238px] max-w-full p-8 rounded flex flex-col items-start justify-start border border-grey-300 hover:!text-white"
            >
              <h3 className="uppercase tracking-widest font-bold mb-0 mt-0 text-white">
                OpenBB Platform
              </h3>
              <p className="text-sm lg:text-base dark:text-grey-300">
                The OpenBB Platform provides a convenient way to access raw financial data from multiple data providers.
              </p>
              <p
                className={clsx(
                  "mt-auto inline-flex items-center gap-1 font-normal text-sm",
                )}
              >
                See more
                <ChevronRightIcon className="group-hover:translate-x-2 tw-transition w-3" />
              </p>
            </Link>
          </div>
          <div className="flex flex-col md:flex-row w-full container items-center justify-center gap-6 px-6 sm:mx-0">
            <Link
              style={{
                backgroundSize: "100% 110%",
              }}
              to="/terminal"
              className="!bg-grey-900 bg-[url('/img/terminal_bg.png')] bg-no-repeat shadow-sm group !no-underline text-white dark:hover:border-white hover:border-grey-600/80 relative w-full h-[238px] max-w-full p-8 rounded flex flex-col items-start justify-start border border-grey-300 hover:!text-white"
            >
              <h3 className="uppercase tracking-widest font-bold mb-0 mt-0 text-white">
                OpenBB Terminal
              </h3>
              <p className="text-sm lg:text-base dark:text-grey-300">
                The OpenBB Terminal is an open source investment research platform accessible to everyone, everywhere.
              </p>
              <p
                className={clsx(
                  "mt-auto inline-flex items-center gap-1 font-normal text-sm",
                )}
              >
                See more
                <ChevronRightIcon className="group-hover:translate-x-2 tw-transition w-3" />
              </p>
            </Link>
            <Link
              style={{
                backgroundSize: "100% 130%",
              }}
              to="/bot"
              className="!bg-grey-900 bg-[url('/img/bot_bg.png')] bg-no-repeat shadow-sm group !no-underline text-white dark:hover:border-white hover:border-grey-600/80 relative w-full h-[238px] max-w-full p-8 rounded flex flex-col items-start justify-start border border-grey-300 hover:!text-white"
            >
              <h3 className="uppercase tracking-widest font-bold mb-0 mt-0 text-white">
                OpenBB Bot
              </h3>
              <p className="text-sm lg:text-base text-grey-300">
                The OpenBB Bot bring market data directly to your financial groups, such as on Discord, Telegram and more.
              </p>
              <p
                className={clsx(
                  "mt-auto inline-flex items-center gap-1 font-normal text-sm",
                )}
              >
                See more
                <ChevronRightIcon className="group-hover:translate-x-2 tw-transition w-3" />
              </p>
            </Link>
          </div>
          <p className="z-20">
            Looking for our website?{" "}
            <a
              href="https://openbb.co"
              className="text-burgundy-300 !underline hover:text-burgundy-400 active:text-burgundy-500"
            >
              Click here
            </a>
          </p>
        </div>
      </article>
    </Layout>
  );
}
