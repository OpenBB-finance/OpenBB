import React from "react"
import clsx from "clsx"
import ChevronRightIcon from "../Icons/ChevronRight"
import Link from "@docusaurus/Link"

export default function ArrowLink({
	label = "Read post",
	url,
	noAnchor = false,
	extraClassNames = "",
	arrowClassNames = "",
}: {
	label?: string | JSX.Element | JSX.Element[]
	url: string
	noAnchor?: boolean
	extraClassNames?: string
	arrowClassNames?: string
}) {
	return noAnchor ? (
		<p
			className={clsx(
				"text-arrow-right mt-auto inline-flex items-center gap-2 font-normal",
				extraClassNames
			)}
		>
			{label}
			<ChevronRightIcon className={clsx("arrow-right", arrowClassNames)} />
		</p>
	) : url.startsWith("https") ? (
		<a
			href={url}
			target="_blank"
			rel="noreferrer"
			className={clsx(
				"text-arrow-right mt-auto inline-flex items-center gap-2 font-normal",
				extraClassNames
			)}
		>
			{label}
			<ChevronRightIcon className={clsx("arrow-right", arrowClassNames)} />
		</a>
	) : (
		<Link
			to={url}
			className={clsx(
				"text-arrow-right mt-auto inline-flex items-center gap-2 font-normal",
				extraClassNames
			)}
		>
			{label}
			<ChevronRightIcon className={clsx("arrow-right", arrowClassNames)} />
		</Link>
	)
}
