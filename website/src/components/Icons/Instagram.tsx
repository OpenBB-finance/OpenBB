import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const InstagramIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 16 17"
    width={16}
    height={17}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <g clipPath="url(#a321222)" strokeLinecap="round">
      <path
        d="M11.334 1.427H4.667A3.333 3.333 0 0 0 1.334 4.76v6.667a3.333 3.333 0 0 0 3.333 3.333h6.667a3.333 3.333 0 0 0 3.333-3.333V4.76a3.333 3.333 0 0 0-3.333-3.333Z"
        fill="#070707"
        stroke="#070707"
      />
      <path
        d="M10.666 7.674a2.667 2.667 0 1 1-5.275.782 2.667 2.667 0 0 1 5.275-.782Z"
        fill="#EAEAEA"
        stroke="#070707"
      />
      <path d="M11.666 4.427h.007" stroke="#EAEAEA" strokeWidth={2} />
    </g>
    <defs>
      <clipPath id="a321222">
        <path fill="#fff" transform="translate(0 .094)" d="M0 0h16v16H0z" />
      </clipPath>
    </defs>
  </svg>
)

export default InstagramIcon
