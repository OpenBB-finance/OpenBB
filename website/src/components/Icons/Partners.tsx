import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}
const PartnersIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 26 23"
    width={26}
    height={23}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M3.278 22.336H.638c0-4.419 3.545-8 7.918-8s7.918 3.581 7.918 8h-2.64c0-2.946-2.363-5.334-5.278-5.334-2.915 0-5.278 2.388-5.278 5.334Zm18.954-4.85-1.866-1.885a9.383 9.383 0 0 0 2.706-6.6 9.38 9.38 0 0 0-2.706-6.6L22.232.516c4.638 4.686 4.638 12.283 0 16.969v.001Zm-3.733-3.77-1.866-1.888a4.03 4.03 0 0 0 0-5.654L18.5 4.285c2.577 2.603 2.577 6.825 0 9.428v.003ZM8.556 13c-2.915 0-5.278-2.388-5.278-5.333 0-2.946 2.363-5.334 5.278-5.334 2.915 0 5.279 2.388 5.279 5.334a5.362 5.362 0 0 1-1.546 3.77A5.251 5.251 0 0 1 8.556 13Zm0-8c-1.442.001-2.615 1.172-2.636 2.628-.02 1.457 1.12 2.66 2.56 2.704 1.442.043 2.65-1.09 2.715-2.545v.533-.653C11.195 6.195 10.014 5 8.556 5Z"
      fill="currentColor"
    />
  </svg>
)

export default PartnersIcon
