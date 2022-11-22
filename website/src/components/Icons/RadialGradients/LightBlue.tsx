import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const LightBlueRadialGradient = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => {
  const id = Math.random() + ""
  return (
    <svg
      viewBox="0 0 1238 1238"
      width={1238}
      height={1238}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-labelledby={titleId}
      {...props}
    >
      {title ? <title id={titleId}>{title}</title> : null}
      <ellipse
        cx={618.937}
        cy={618.743}
        rx={618.773}
        ry={618.389}
        transform="rotate(28.28 618.937 618.743)"
        fill={`url(#${id})`}
      />
      <defs>
        <radialGradient
          id={id}
          cx={0}
          cy={0}
          r={1}
          gradientUnits="userSpaceOnUse"
          gradientTransform="rotate(92.768 14.694 604.239) scale(633.303 633.695)"
        >
          <stop stopColor="#0097DE" stopOpacity={0.5} />
          <stop offset={1} stopOpacity={0} />
        </radialGradient>
      </defs>
    </svg>
  )
}

export default LightBlueRadialGradient
