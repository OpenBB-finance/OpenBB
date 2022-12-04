import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const DarkPurpleRadialGradient = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => {
  const id = Math.random() + ""
  return (
    <svg
      viewBox="0 0 1676 1676"
      width={1676}
      height={1676}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-labelledby={titleId}
      {...props}
    >
      {title ? <title id={titleId}>{title}</title> : null}
      <ellipse
        cx={837.937}
        cy={838.228}
        rx={618.773}
        ry={618.389}
        transform="rotate(28.28 837.937 838.228)"
        fill={`url(#${id})`}
      />
      <defs>
        <radialGradient
          id={id}
          cx={0}
          cy={0}
          r={1}
          gradientUnits="userSpaceOnUse"
          gradientTransform="rotate(92.768 19.63 818.315) scale(633.303 633.695)"
        >
          <stop stopColor="#472C75" stopOpacity={0.8} />
          <stop offset={1} stopOpacity={0} />
        </radialGradient>
      </defs>
    </svg>
  )
}

export default DarkPurpleRadialGradient
