import React, { SVGProps } from "react";
interface SVGRProps {
	title?: string;
	titleId?: string;
}

const CurvedArrowPricing = ({
	title,
	titleId,
	...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
	<svg
		viewBox="0 0 33 20"
		width={33}
		height={20}
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		aria-labelledby={titleId}
		{...props}
	>
		{title ? <title id={titleId}>{title}</title> : null}
		<path
			d="M1.208 17.298a.75.75 0 1 0-.416 1.441l.416-1.441ZM28.591.538a.75.75 0 0 0-1.052-.13L22.216 4.56a.75.75 0 0 0 .923 1.183l4.73-3.69 3.69 4.73a.75.75 0 0 0 1.184-.922L28.59.54ZM1 18.019l-.208.721h.001l.002.001.007.002.025.007.09.025.341.087c.294.072.72.17 1.255.275 1.068.209 2.574.444 4.332.553 3.5.217 8.07-.065 12.166-2.136l-.677-1.338c-3.759 1.9-8.025 2.186-11.397 1.977a32.16 32.16 0 0 1-4.136-.528 25.398 25.398 0 0 1-1.495-.339 6.99 6.99 0 0 1-.076-.02l-.018-.006-.004-.001-.208.72Zm18.011-.465c4.174-2.11 6.596-6.292 7.97-9.829a32.146 32.146 0 0 0 1.68-6.081 19.142 19.142 0 0 0 .082-.539v-.008l.001-.003L28 1l-.744-.092-.001.005-.003.022-.013.093a26.787 26.787 0 0 1-.324 1.734 30.644 30.644 0 0 1-1.332 4.42c-1.326 3.412-3.568 7.172-7.249 9.033l.677 1.338Z"
			fill="currentColor"
		/>
	</svg>
);

export default CurvedArrowPricing;
