import React from "react";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";
import DarkBlueRadialGradient from "../components/Icons/RadialGradients/DarkBlue";
import RubyRedRadialGradient from "../components/Icons/RadialGradients/RubyRed";
import { useIFrameContext } from "@site/src/theme/Root";

export default function NotFound() {
  const { isIFrame } = useIFrameContext();
  return (
    <Layout title="404 | OpenBB Docs">
      <div className="flex flex-col items-center justify-center my-auto p-10 relative overflow-hidden min-h-[60vh] 2xl:min-h-[70vh]">
        <DarkBlueRadialGradient className="absolute opacity-40 -left-[1000px] w-[1600px] h-[1600px] lg:-left-[1000px] lg:opacity-40 -top-20 xl:-top-60 xl:-left-[800px] 2xl:opacity-50" />
        <RubyRedRadialGradient className="absolute opacity-40 -right-[1000px] w-[1600px] h-[1600px] lg:-right-[1000px] lg:opacity-40 -top-20 xl:-top-60 xl:-right-[800px] 2xl:opacity-50" />

        <img
          src="/img/404.png"
          className="shadow-none"
          width={612}
          height={271}
          alt="not found"
        />
        <div className="mt-8 flex-center flex-col gap-0">
          <h1 className="uppercase text-center tracking-widest font-bold text-2xl">
            OOPS! PAGE NOT FOUND!
          </h1>
          <p className="text-center text-xl mt-6">
            Sorry the page you’re looking for doesn’t exist.
            <br />
            If you think something is broken, please report a problem.
          </p>
          <div className="flex flex-col md:flex-row gap-6 mt-10 justify-center w-full">
            <Link
              to={isIFrame ? "/terminal/usage/basics" : "/"}
              className="_btn"
            >
              Return Home
            </Link>
            <a
              // TODO - add link to report problem
              href="https://openbb.co/support"
              target="_blank"
              rel="noopener noreferrer"
              className="_btn-secondary"
            >
              Report problem
            </a>
          </div>
        </div>
      </div>
    </Layout>
  );
}
