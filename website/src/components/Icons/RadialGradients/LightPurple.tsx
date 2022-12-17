import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const LightPurpleRadialGradient = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => {
  const id = Math.random() + ""
  return (
    <svg
      width={1677}
      height={1676}
      viewBox="0 0 1677 1676"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-labelledby={titleId}
      {...props}
    >
      {title ? <title id={titleId}>{title}</title> : null}
      <ellipse
        cx={838.735}
        cy={838.228}
        rx={618.773}
        ry={618.389}
        transform="rotate(28.28 838.735 838.228)"
        fill={`url(#${id})`}
      />
      <defs>
        <radialGradient
          id={id}
          cx={0}
          cy={0}
          r={1}
          gradientUnits="userSpaceOnUse"
          gradientTransform="rotate(92.768 20.028 818.695) scale(633.303 633.695)"
        >
          <stop stopColor="#822661" stopOpacity={0.5} />
          <stop offset={1} stopOpacity={0} />
        </radialGradient>
      </defs>
    </svg>
  )
}

export default LightPurpleRadialGradient
