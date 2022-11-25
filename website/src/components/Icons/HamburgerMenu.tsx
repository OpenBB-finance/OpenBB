import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const HamburgerMenuIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    width={32}
    height={22}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 32 22"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M1 1h30M1 11h30M1 21h30"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
)

export default HamburgerMenuIcon
