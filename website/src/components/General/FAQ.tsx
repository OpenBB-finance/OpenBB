import React from "react"
import * as AccordionPrimitive from "@radix-ui/react-accordion"
import clsx from "clsx"
import ChevronRightIcon from "../Icons/ChevronRight"
import { useLocation } from "@docusaurus/router"

export default function FAQ({ items }: { items: AccordionItem[] }) {
  const { hash } = useLocation()
  const selectedQuestion = hash.substring(1)
  return (
    <AccordionPrimitive.Root
      type="multiple"
      defaultValue={[selectedQuestion]}
      className="space-y-12 mt-12 text-sm"
    >
      {items.map(({ question, answer }, i) => (
        <AccordionPrimitive.Item
          id={`faq-${i + 1}`}
          key={`header-${i}`}
          value={`faq-${i + 1}`}
          style={{
            transition: "border-color 0.5s ease",
          }}
          className="rounded-md border text-sm dark:radix-state-open:border-white dark:radix-state-closed:border-grey-600 lg:w-[776px] dark:bg-grey-900"
        >
          <AccordionPrimitive.Header className="w-full rounded-md">
            <AccordionPrimitive.Trigger
              style={{
                transition: "color 0.5s ease",
              }}
              className={clsx(
                "group",
                "radix-state-open:rounded-t-lg dark:radix-state-open:text-white dark:radix-state-closed:rounded-lg dark:radix-state-closed:text-grey-400",
                "focus:outline-none",
                "inline-flex w-full items-center justify-between p-6 text-left"
              )}
            >
              <span
                className="text-sm"
                style={{ fontFamily: "Fira Code, sans-serif", fontWeight: 500 }}
              >
                {question}
              </span>
              <ChevronRightIcon
                className={clsx(
                  "ml-2 h-5 w-5 shrink-0 ease-in-out",
                  "group-radix-state-open:rotate-90 group-radix-state-open:duration-300"
                )}
              />
            </AccordionPrimitive.Trigger>
          </AccordionPrimitive.Header>
          <AccordionPrimitive.Content asChild>
            <div className="pt-r1 w-full text-left rounded-b-lg p-6 pt-0 dark:text-grey-400" dangerouslySetInnerHTML={{ __html: answer }} />
          </AccordionPrimitive.Content>
        </AccordionPrimitive.Item>
      ))}
    </AccordionPrimitive.Root>
  )
}
export interface AccordionItem {
  question: string
  answer: string
}