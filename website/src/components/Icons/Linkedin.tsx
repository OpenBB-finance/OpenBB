import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const LinkedinIcon = ({
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
      d="M13 21H9V9h4v2a4.618 4.618 0 0 1 3.525-1.763A4.5 4.5 0 0 1 21 13.75V21h-4v-6.75a2.265 2.265 0 0 0-2.247-1.944A1.815 1.815 0 0 0 13 14.25V21Zm-6 0H3V9h4v12ZM5 7a2 2 0 1 1 0-4 2 2 0 0 1 0 4Z"
      fill="currentColor"
    />
  </svg>
)

export default LinkedinIcon
