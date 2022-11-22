import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const StarIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 24 24"
    width={24}
    height={24}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="m12 1 3.263 7.439L23 9.403l-5.72 5.562L18.798 23 12 18.999 5.202 23l1.518-8.035L1 9.403l7.737-.964L12 1Z"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinejoin="round"
    />
  </svg>
)

export default StarIcon
