import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const BulbIcon = ({
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
      d="M9.663 17h4.673-4.673ZM12 3v1-1Zm6.364 2.636-.707.707.707-.707ZM21 12h-1 1ZM4 12H3h1Zm2.343-5.657-.707-.707.707.707Zm2.121 9.193a5 5 0 1 1 7.072 0l-.548.547A3.373 3.373 0 0 0 14 18.469V19a2 2 0 0 1-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547Z"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
)

export default BulbIcon
