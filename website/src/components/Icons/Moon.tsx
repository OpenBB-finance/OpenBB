import React, { SVGProps } from "react";;
interface SVGRProps {
	title?: string;
	titleId?: string;
}

const MoonIcon = ({
	title,
	titleId,
	...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
	<svg
		viewBox="0 0 24 24"
		width={24}
		height={24}
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		aria-labelledby={titleId}
		{...props}
	>
		{title ? <title id={titleId}>{title}</title> : null}
		<path
			d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z"
			stroke="currentColor"
			strokeWidth={1.5}
			strokeLinecap="round"
			strokeLinejoin="round"
		/>
	</svg>
);

export default MoonIcon;