import React from "react";
import clsx from "clsx";
import Link from "@docusaurus/Link";
import Layout from "@theme/Layout";
import ChevronRightIcon from "../components/Icons/ChevronRight";
import RubyRedRadialGradient from "../components/Icons/RadialGradients/RubyRed";
import DarkBlueRadialGradient from "../components/Icons/RadialGradients/DarkBlue";
import FAQ, { AccordionItem } from "../components/General/FAQ";

export default function Home(): JSX.Element {
    return (
        <Layout description="Documentation for free and open source OpenBB products.">
            <main className="relative py-20 md:py-0 flex flex-col items-center justify-center my-32 overflow-hidden">
                <DarkBlueRadialGradient className="absolute opacity-40 -left-[1000px] w-[1600px] h-[1600px] lg:-left-[1000px] lg:opacity-40 -top-20 xl:-top-60 xl:-left-[800px] 2xl:opacity-50" />
                <RubyRedRadialGradient className="absolute opacity-40 -right-[1000px] w-[1600px] h-[1600px] lg:-right-[1000px] lg:opacity-40 -top-20 xl:-top-60 xl:-right-[800px] 2xl:opacity-50" />
                <div className="relative z-10 flex flex-col items-center justify-center w-full max-w-4xl px-4 mx-auto">
                    <h1 className="text-4xl font-bold text-center text-gray-900 dark:text-gray-100">Frequently Asked Questions</h1>
                    <p className="mt-4 text-xl text-center text-gray-600 dark:text-gray-400">Here are some of the most frequently asked questions about OpenBB.</p>
                    <FAQ items={FAQ_items} />
                </div>
            </main>
        </Layout>
    );
}

const FAQ_items: AccordionItem[] = [
    {
      header: "How Do I Link My OpenBB Bot Account?",
      content:
        'After you signup for an OpenBB Bot plan you can link your accounts from <a href="https://my.openbb.co/app" class="_hyper-link">here</a>',
    },
    {
      header: "Can I try an OpenBB Bot plan?",
      content:
        "You can try a preview of any plan by just running commands on a server that has OpenBB Bot, like <a href='https://my.openbb.co/discord' class='_hyper-link'>OpenBB Discord</a>. We offer a limited amount of daily commands.",
    },
    {
      header: "Will my OpenBB Bot plan renew at the end of the billing cycle?",
      content:
        "Yes, plans renew automatically at the end of the monthly and yearly billing cycles. You can cancel your plan at any time, before the end of the billing cycle, and it will not auto-renew anymore.",
    },
    {
      header: "Can I get a refund on my OpenBB Bot?",
      content:
        "Since we offer a free command tier to try commands we don't offer refunds as you have had ample time to try the service and make a decision.",
    },
    {
      header: "If I sign up for OpenBB Bot do I get access on all platforms?",
      content:
        "Yes! You will have access on Discord, and other platforms as we add support.",
    },
    {
      header: "If I cancel OpenBB Bot subscription do I still have access?",
      content:
        "No, you will lose your access but you get a credit on your account of the prorated amount until the end of your current billing cycle.",
    },
    {
      header:
        "What's the difference in an individual plan and server plan on OpenBB Bot?",
      content:
        "An individual plan gives your account access to OpenBB Bot while a server plan gives the whole server access. An individual plan carries more perks with it than a server plan, which you can find by clicking on the plan.",
    },
    {
      header: "I added the bot but still don't see slash commands, what do I do?",
      content: `
        <img class="mb-8" src="https://assets-global.website-files.com/5f9072399b2640f14d6a2bf4/625ddbedd330d37960463537_Untitled.png" />
        Just head to <b>Server Settings → Integrations</b> and then <b>click ‘Manage’ next to an app</b>, where you will behold a new, shiny, and dare we say <i>dazzling</i>, new surface.
  <ul class="list-disc my-4 ml-4">
  <li>Use toggles to modify which members can use commands</li>
  <li>Use toggles to modify which channels allow commands</li>
  </ul>
  There’s also a command-specific list, where you can make customized permissions for each command.
  <ul class="list-disc my-4 ml-4">
  <li>By default, these are all synced to the command permission at the top.</li>
  <li>You can unsync an individual command to make further customizations.</li>
  </ul>
  For more information click <a rel="noreferrer noopener" target="_blank" href="https://discord.com/blog/slash-commands-permissions-discord-apps-bots" class="_hyper-link">here</a>.
        `,
    },
  ]
  