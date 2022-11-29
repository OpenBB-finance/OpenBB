import React from "react";
import Translate, { translate } from "@docusaurus/Translate";
import { PageMetadata } from "@docusaurus/theme-common";
import Layout from "@theme/Layout";
export default function NotFound() {
  return (
    <>
      <PageMetadata
        title={translate({
          id: "theme.NotFound.title",
          message: "Page Not Found",
        })}
      />
      <Layout>
        <main className="container margin-vert--xl mb-20">
          <div className="row">
            <div className="col col--6 col--offset-3">
              <h1 className="mt-10 !text-[32px] uppercase font-bold tracking-widest">
                <Translate
                  id="theme.NotFound.title"
                  description="The title of the 404 page"
                >
                  Page Not Found
                </Translate>
              </h1>
              <p className="mt-6 mb-2">
                We could not find what you were looking for.
              </p>
              <p>
                We recently moved our documentation to a new location and some
                links may be broken. Popular links are listed below:
              </p>
              <ul className="space-y-1 max-w-md list-disc list-inside mt-4">
                <li>
                  <a href="/">Homepage</a>
                </li>
                <li>
                  <a href="/sdk">Terminal Documentation</a>
                  <ul className="space-y-1 max-w-md list-disc ml-4 mt-2 mb-3 list-inside">
                    <li>
                      <a href="/terminal/quickstart/installation">
                        Terminal Installation
                      </a>
                    </li>
                    <li>
                      <a href="/terminal/reference">Terminal Reference</a>
                    </li>
                  </ul>
                </li>
                <li>
                  <a href="/sdk">SDK Documentation</a>
                  <ul className="space-y-1 max-w-md list-disc ml-4 mt-2 mb-3 list-inside">
                    <li>
                      <a href="/sdk/quickstart/installation">
                        SDK Installation
                      </a>
                    </li>
                    <li>
                      <a href="/sdk/reference">SDK Reference</a>
                    </li>
                  </ul>
                </li>
              </ul>
            </div>
          </div>
        </main>
      </Layout>
    </>
  );
}
