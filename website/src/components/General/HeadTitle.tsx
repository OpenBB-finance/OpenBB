import * as React from "react";
import Head from "@docusaurus/Head";

export default function HeadTitle({ title }: { title: string }) {
    return (
        <Head>
            <title>{title}</title>
        </Head>
    );
}
