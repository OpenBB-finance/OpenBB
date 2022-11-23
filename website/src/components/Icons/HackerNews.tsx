import React, { SVGProps } from "react"
interface SVGRProps {
	title?: string;
	titleId?: string;
}

const HackerNewsIcon = ({
	title,
	titleId,
	...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
	<svg
		xmlns="http://www.w3.org/2000/svg"
		width={30.961}
		height={30.961}
		viewBox="0 0 31 31"
		xmlSpace="preserve"
		aria-labelledby={titleId}
		{...props}
	>
		{title ? <title id={titleId}>{title}</title> : null}
		<path fill="currentColor" d="M21.27 0a3114.32 3114.32 0 0 1-5.532 9.499h-.11c-.033-.035-4.204-7.426-5.375-9.499H3.148l9.253 15.034v15.927h6.157V15.034L27.812 0H21.27z" />
	</svg>
)

export default HackerNewsIcon
