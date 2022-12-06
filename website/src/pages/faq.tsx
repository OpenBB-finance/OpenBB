import React from "react";
import clsx from "clsx";
import Link from "@docusaurus/Link";
import Layout from "@theme/Layout";
import ChevronRightIcon from "../components/Icons/ChevronRight";
import RubyRedRadialGradient from "../components/Icons/RadialGradients/RubyRed";
import DarkBlueRadialGradient from "../components/Icons/RadialGradients/DarkBlue";
import FAQ, { AccordionItem } from "../components/General/FAQ";
import FAQContent from "../../content/faq.json";

export default function Home(): JSX.Element {
    return (
        <Layout description="Documentation for free and open source OpenBB products.">
            <main className="relative py-20 md:py-0 flex flex-col items-center justify-center my-32 overflow-hidden min-h-[80vh]">
                <DarkBlueRadialGradient className="absolute opacity-40 -left-[1000px] w-[1600px] h-[1600px] lg:-left-[1000px] lg:opacity-40 -top-20 xl:-top-60 xl:-left-[800px] 2xl:opacity-50" />
                <RubyRedRadialGradient className="absolute opacity-40 -right-[1000px] w-[1600px] h-[1600px] lg:-right-[1000px] lg:opacity-40 -top-20 xl:-top-60 xl:-right-[800px] 2xl:opacity-50" />
                <div className="relative z-10 flex flex-col items-center justify-center w-full max-w-4xl px-4 mx-auto">
                    <h1 className="text-4xl font-bold text-center text-gray-900 dark:text-gray-100">Frequently Asked Questions</h1>
                    <p className="mt-4 text-xl text-center text-gray-600 dark:text-gray-400">Here are some of the most frequently asked questions about OpenBB.</p>
                    <FAQ items={FAQContent} />
                </div>
            </main>
        </Layout>
    );
}