import React from "react";
import clsx from "clsx";
import Link from "@docusaurus/Link";
import Layout from "@theme/Layout";
import ChevronRightIcon from "../components/Icons/ChevronRight";
import RubyRedRadialGradient from "../components/Icons/RadialGradients/RubyRed";
import DarkBlueRadialGradient from "../components/Icons/RadialGradients/DarkBlue";

export default function Home(): JSX.Element {
  return (
    <Layout description="Documentation for free and open source OpenBB products.">
      <main className="relative min-h-[75vh] py-20 md:py-0 flex flex-col items-center justify-center overflow-hidden">
        <DarkBlueRadialGradient className="absolute opacity-40 -left-[1000px] w-[1600px] h-[1600px] lg:-left-[1000px] lg:opacity-40 -top-20 xl:-top-60 xl:-left-[800px] 2xl:opacity-50" />
        <RubyRedRadialGradient className="absolute opacity-40 -right-[1000px] w-[1600px] h-[1600px] lg:-right-[1000px] lg:opacity-40 -top-20 xl:-top-60 xl:-right-[800px] 2xl:opacity-50" />
        <div className="flex mx-auto flex-col items-center justify-center w-full max-w-[906px]">
          <div className="z-10 flex flex-col items-center justify-center w-full h-full mb-10 md:mb-0">
            <h1 className="mx-6 font-bold text-2xl lg:text-3xl xl:text-4xl leading-10 text-center mb-4 tracking-widest uppercase">
              OpenBB Documentation
            </h1>
            <p className="mx-6 w-[315px] md:w-[880px] text-sm lg:text-lg xl:text-xl text-center text-grey-900 dark:text-white">
              This website contains documentation for OpenBB SDK and Terminal, two
              open source projects that powers your investment research.
            </p>
          </div>
          <div className="flex flex-col md:flex-row w-full container items-center justify-center gap-6 px-6 sm:mx-0 mt-8 md:!mt-14 lg:!mt-15 md:mb-0">
            <Link
              style={{
                backgroundSize: "100% 110%",
              }}
              to="/terminal"
              className="bg-[url('/img/terminal_bg_light.png')] dark:bg-[url('/img/terminal_bg.png')] bg-no-repeat shadow-sm group !no-underline text-grey-900 dark:text-white hover:text-grey-900 dark:hover:border-white hover:border-grey-900 dark:hover:!text-white relative w-full h-[238px] max-w-full p-8 rounded flex flex-col items-start justify-start border border-grey-400 bg-white dark:bg-grey-900"
            >
              <h3 className="uppercase tracking-widest font-bold text-2xl mb-3">
                OpenBB Terminal
              </h3>
              <p className="text-sm lg:text-base dark:text-grey-300">
                Desktop application that allows you to perform your own investment
                research.
              </p>
              <p
                className={clsx(
                  "mt-auto inline-flex items-center gap-2 font-normal",
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
              to="/sdk"
              className="bg-[url('/img/sdk_bg_light.png')] dark:bg-[url('/img/sdk_bg.png')] bg-no-repeat shadow-sm group !no-underline text-grey-900 dark:text-white hover:text-grey-900 dark:hover:border-white hover:border-grey-900 dark:hover:!text-white relative w-full h-[238px] max-w-full p-8 rounded flex flex-col items-start justify-start border border-grey-400 bg-white dark:bg-grey-900"
            >
              <h3 className="uppercase tracking-widest font-bold text-2xl mb-3">
                OpenBB SDK
              </h3>
              <p className="text-sm lg:text-base dark:text-grey-300">
                Python library that allows you to build your own investment
                research platform.
              </p>
              <p
                className={clsx(
                  "mt-auto inline-flex items-center gap-2 font-normal",
                )}
              >
                See more
                <ChevronRightIcon className="group-hover:translate-x-2 tw-transition w-3" />
              </p>
            </Link>
          </div>
        </div>
      </main>
    </Layout>
  );
}
