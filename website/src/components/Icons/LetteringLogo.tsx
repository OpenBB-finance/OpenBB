import React, { SVGProps } from "react";
interface SVGRProps {
	title?: string;
	titleId?: string;
}

const LetteringLogo = ({
	title,
	titleId,
	...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
	<svg
		viewBox="0 0 170 17"
		width={170}
		height={17}
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		aria-labelledby={titleId}
		{...props}
	>
		{title ? <title id={titleId}>{title}</title> : null}
		<path
			d="M106.107 1.889v11.334l-.961-.946-.959-.945-.962-.943-.959-.946-.961-.943-.962-.945-.959-.944-.961-.945-.96-.943-.961-.946-.96-.943-.96-.945H92.66V17H94.582V4.723l.96.943.96.945.961.944.96.945.961.943.959.946.962.943.961.945.959.946.962.943.959.945.961.944.96.945h.961V1.889H106.107ZM137.03 7.557h-1.921V1.889h-11.524V17h15.37V7.546h-1.92l-.005.01Zm-11.524-.946V3.773h7.683v3.78h-7.683V6.61Zm11.524 3.778v4.727h-11.524v-5.67h11.524v.943ZM168.901 7.557h-2.88V1.889h-11.526V0h-1.921v1.889h1.921V17h15.365V7.546l-.959.01Zm-12.485-.946V3.773h7.684v3.78h-7.684V6.61Zm11.526 3.778v4.727h-11.526v-5.67h11.526v.943ZM75.314 1.889H61.867V17H77.23V15.111H63.787V11.332h11.521V9.443H63.788V3.777H77.23V1.89h-1.916ZM13.444 1.889H0V17h15.367V1.889h-1.922Zm0 2.834V15.11H1.918V3.773h11.527v.95ZM44.397 1.889H30.952V17h1.92v-5.666h13.445V1.88h-1.92v.009Zm0 2.834V9.45H32.873V3.773h11.524v.95Z"
			fill="currentColor"
		/>
	</svg>
);

export default LetteringLogo;
