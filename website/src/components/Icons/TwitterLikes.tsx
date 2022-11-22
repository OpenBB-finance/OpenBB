import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const TwitterLikesIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 18 18"
    width={18}
    height={18}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M15.63 3.457a4.125 4.125 0 0 0-5.834 0L9 4.252l-.795-.795A4.126 4.126 0 0 0 2.37 9.292l.795.795L9 15.922l5.835-5.835.795-.795a4.127 4.127 0 0 0 0-5.835v0Z"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
)

export default TwitterLikesIcon
