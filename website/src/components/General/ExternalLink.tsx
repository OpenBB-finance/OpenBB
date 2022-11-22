import clsx from "clsx"
import React, { forwardRef } from "react"

const ExternalLink = forwardRef<
	HTMLAnchorElement,
	{
		children: JSX.Element | JSX.Element[] | string
		href: string
		type?: "link" | "button"
		extraClassNames?: string
	}
>(({ children, href, type = "link", extraClassNames = "" }, ref) => {
	return (
		<a
			ref={ref}
			className={clsx(
				{
					_btn: type === "button",
					"_hyper-link": type !== "button",
				},
				extraClassNames
			)}
			href={href}
			target="_blank"
			rel="noreferrer"
		>
			{children}
		</a>
	)
})

export default ExternalLink
