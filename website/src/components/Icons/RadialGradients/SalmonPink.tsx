import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const SalmonPinkRadialGradient = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => {
  const id = Math.random() + ""
  return (
    <svg
      width={1676}
      height={1677}
      viewBox="0 0 1676 1677"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-labelledby={titleId}
      {...props}
    >
      {title ? <title id={titleId}>{title}</title> : null}
      <ellipse
        cx={837.899}
        cy={838.714}
        rx={618.773}
        ry={618.389}
        transform="rotate(28.28 837.899 838.714)"
        fill={`url(#${id})`}
      />
      <defs>
        <radialGradient
          id={id}
          cx={0}
          cy={0}
          r={1}
          gradientUnits="userSpaceOnUse"
          gradientTransform="rotate(92.768 19.379 818.54) scale(633.303 633.695)"
        >
          <stop stopColor="#D70043" stopOpacity={0.5} />
          <stop offset={1} stopOpacity={0} />
        </radialGradient>
      </defs>
    </svg>
  )
}

export default SalmonPinkRadialGradient
