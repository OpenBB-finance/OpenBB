import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const BurgundyRadialGradient = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 1239 1238"
    width={1239}
    height={1238}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <ellipse
      cx={619.735}
      cy={619.228}
      rx={618.773}
      ry={618.389}
      transform="rotate(28.28 619.735 619.228)"
      fill="url(#aodkowakdowakdoawkda)"
    />
    <defs>
      <radialGradient
        id="aodkowakdowakdoawkda"
        cx={0}
        cy={0}
        r={1}
        gradientUnits="userSpaceOnUse"
        gradientTransform="rotate(92.768 14.862 604.861) scale(633.303 633.695)"
      >
        <stop stopColor="#822661" stopOpacity={0.5} />
        <stop offset={1} stopOpacity={0} />
      </radialGradient>
    </defs>
  </svg>
)

export default BurgundyRadialGradient
